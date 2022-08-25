#!/bin/env python3
# -*- coding: utf-8 -*-
import json
import types
import base64
import logging
import aiohttp
import marshal

from urllib.parse import urlparse
from helpers import is_url, preprocess_url
from aiorobotparser import AIORobotFileParser


log = logging.getLogger(__name__)

class Spider:
    def __init__(
            self, 
            consumer, 
            producer, 
            redis, 
            task_topic_name, 
            result_topic_name, 
            old_urls_key,
            timeout=30,
            headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47'}
        ):
        self.consumer = consumer
        self.producer = producer
        self.redis = redis
        self.task_topic_name = task_topic_name
        self.result_topic_name = result_topic_name
        self.old_urls_key = old_urls_key
        self.timeout = timeout
        self.headers = headers
        self.session = aiohttp.ClientSession(timeout=self.timeout, headers=self.headers)
        self.msg = None
        self.task = None
        self.stop = False
        self.use_robots = False
        self.use_tor = False
        self.use_proxy = False
        self.generator_id = None
        self.matcher_id = None
        self.netloc = None
        self.scheme = None
        self.payload = None

    async def get_task(self):
        self.msg = await self.consumer.__anext__()
        self.task = json.loads(self.msg.value)

    async def publish_task(self, task):
        if await self.is_valid_task(task):
            await self.producer_send(self.task_topic_name, task)
    
    async def producer_send(self, topic_name, data):
        await self.producer.send_and_wait(topic_name, json.dumps(data).encode())
    
    async def process_payload(self, payload):
        return base64.b64encode(json.dumps(payload).encode()).decode()

    async def publish_tasks(self, next_urls):
        task = self.task.copy()
        for next_url in next_urls:
            task['url'] = next_url.get('url')
            if 'method' in next_url:
                task['method'] = next_url.get('method')
            if 'headers' in next_url:
                task['headers'] = next_url.get('headers')
            if 'payload' in next_url:
                task['payload'] = await self.process_payload(next_url.get('payload'))
            await self.publish_task(task)

    async def add_old_urls(self, old_urls):
        for old_url in old_urls:
            await self.redis.sadd(self.old_urls_key, preprocess_url(old_url))

    async def deliver_result(self, result):
        result['id'] = self.task.get('id')
        log.info('Result %s', result)
        await self.producer_send(self.result_topic_name, result)

    async def deliver_results(self, results):
        for result in results:
            await self.deliver_result(result)

    async def get_data(self):
        log.info('URL = %s', self.url)
        method = 'GET'
        if 'method' in self.task:
            method = self.task.get('method')
        headers = self.headers
        if 'headers' in self.task:
            headers = json.loads(self.task.get('headers'))
            headers.update(self.headers)
        timeout = self.timeout
        if 'timeout' in self.task:
            timeout = self.task.get('timeout')
        self.payload = None
        if 'payload' in self.task:
            self.payload = base64.b64decode(self.task.get('payload'))
        log.info('Method %s', method)
        log.info('Headers %s', headers)
        log.info('Timeout %s', timeout)
        log.info('Payload %s', self.payload)
        async with self.session.request(method, self.url, timeout=timeout, headers=headers, data=self.payload) as resp:
            self.resp_raw = await resp.read()

    async def get_robots(self):
        self.use_robots = self.task.get('use_robots')
        if not self.use_robots:
            return
        if not self.url:
            raise Exception('The url must be initialized first. ')
        url_parse = urlparse(self.url)
        if url_parse.scheme:
            self.scheme = url_parse.scheme
        else:
            self.scheme = 'http'
        if not url_parse.netloc:
            raise Exception('Unexpected URL %s', self.url)
        if self.netloc != url_parse.netloc:
            self.netloc = url_parse.netloc
            try:
                self.robot_parser = AIORobotFileParser()
                robot_url = '{}://{}/robots.txt'.format(self.scheme, self.netloc)
                log.info('Robot url %s', robot_url)
                self.robot_parser.set_url(robot_url)
                await self.robot_parser.read()
                log.info('Crawl delay %s', self.robot_parser.crawl_delay('*'))
                log.info('Request rate %s', self.robot_parser.request_rate("*"))
            except:
                self.robot_parser = None

    async def create_tasks(self):
        generator_id = self.task.get('generator')
        if not generator_id:
            return
        if self.generator_id != generator_id:
            self.generator_id = generator_id
            await self.get_generator()
        log.info('Generator %s', self.generator)
        try:
            next_urls, old_urls = await self.generator.generate(self.url, self.payload, self.resp_raw)
            log.info('Next urls %s', next_urls)
        except Exception as e:
            log.error(e, exc_info=True)
            next_urls = set()
            old_urls = set()
        if not next_urls:
            return
        await self.publish_tasks(next_urls)
        await self.add_old_urls(old_urls)

    async def get_generator(self):
        generator_code_bin = await self.redis.get(self.generator_id)
        self.generator = await self.get_component('generator', generator_code_bin)

    async def get_component(self, component_type, c_code_bin):
        c_code = marshal.loads(c_code_bin)
        c_module = types.ModuleType(component_type)
        exec(c_code, c_module.__dict__)
        return c_module

    async def get_matcher(self):
        matcher_code_bin = await self.redis.get(self.matcher_id)
        self.matcher = await self.get_component('matcher', matcher_code_bin)

    async def create_results(self):
        matcher_id = self.task.get('matcher')
        if not matcher_id:
            return
        if self.matcher_id != matcher_id:
            self.matcher_id = matcher_id
            await self.get_matcher()
            log.info('Got matcher')
        try:
            results = await self.matcher.match(self.url, self.resp_raw)
        except:
            results = set()
        if not results:
            return
        await self.deliver_results(results)
    
    async def is_valid_task(self, task):
        return {'id', 'url', 'generator', 'matcher'} <= task.keys()

    async def is_invalid_task(self):
        if not await self.is_valid_task(self.task):
            return True
        url = self.task.get('url')
        if not is_url(url):
            return True
        url = preprocess_url(url)
        log.info('URL = %s. ', url)
        if (await self.redis.sismember(self.old_urls_key, url)):
            return True
        self.url = url
        await self.get_robots()
        return self.use_robots and self.robot_parser and not self.robot_parser.can_fetch('*', self.url)
    
    async def close(self):
        await self.session.close()

    async def working(self):
        log.info('Start working')
        while True:
            try:
                await self.get_task()
                log.info('Got task %s', self.task)
                if (await self.is_invalid_task()):
                    continue
                await self.get_data()
                log.info('Got data')
                await self.create_tasks()
                log.info('Created tasks')
                await self.create_results()
                log.info('Created results')
                if self.stop:
                    break
            except Exception as e:
                log.error(e, exc_info=True)
    
