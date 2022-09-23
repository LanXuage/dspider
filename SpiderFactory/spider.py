#!/bin/env python3
# -*- coding: utf-8 -*-
import re
import zstd
import json
import types
import base64
import logging
import asyncio
import aiohttp
import marshal

from time import time
from io import StringIO
from aioredis import Redis
from aioredis.lock import Lock
from common.helpers import is_url
from common.net import Request, Response
from aiorobotparser import AIORobotFileParser
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer


log = logging.getLogger(__name__)


class Spider:
    def __init__(
        self,
        consumer: AIOKafkaConsumer,
        producer: AIOKafkaProducer,
        redis: Redis,
        task_topic_name: str,
        result_topic_name: str,
        old_urls_key: str,
        timeout=30,
        headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47'}
    ):
        self.consumer = consumer
        self.producer = producer
        self.redis = redis
        self.task_topic_name = task_topic_name
        self.result_topic_name = result_topic_name
        self.old_urls_key = old_urls_key
        self.timeout = timeout
        self.headers = headers
        self.session = aiohttp.ClientSession(
            timeout=self.timeout, headers=self.headers)
        self.msg = None
        self.task = None
        self.stop = False
        self.use_robots = False
        self.use_tor = False
        self.use_proxy = False
        self.generator_id = None
        self.generator_cfg = dict()
        self.g_log_state = 0
        self.matcher_id = None
        self.matcher_cfg = dict()
        self.m_log_state = 0
        self.req = None
        self.resp = None
        self.re_match_site = re.compile(r'^https?://[\w.-]+(/|$)')
        self.has_ret_log = False
        self.task_lock: Lock = None
        self.next_reqs = None
        self.results = None

    async def get_task(self):
        log.info('Wait for task. ')
        self.msg = await self.consumer.__anext__()
        self.task = json.loads(zstd.uncompress(self.msg.value))
        if self.task_lock:
            try:
                await self.task_lock.release()
            except:
                pass
        self.task_lock = self.redis.lock(
            'lanxuage_ds_task_lock_' + str(self.task.get('id')))

    async def publish_task(self, task):
        if await self.is_valid_task(task):
            await self.producer_send(self.task_topic_name, task)

    async def producer_send(self, topic_name, data):
        await self.producer.send_and_wait(topic_name, zstd.compress(json.dumps(data).encode(), 18))

    async def process_payload(self, payload):
        return base64.b64encode(payload).decode()

    async def publish_tasks(self, next_reqs):
        task = self.task.copy()
        for next_req in next_reqs:
            if not isinstance(next_req, Request):
                continue
            task['url'] = next_req.url
            task['method'] = next_req.method
            task['headers'] = next_req.headers
            task['payload'] = await self.process_payload(next_req.payload)
            await self.publish_task(task)

    async def add_old_urls(self, old_reqs):
        for old_req in old_reqs:
            if not isinstance(old_req, Request):
                continue
            await self.redis.sadd(self.old_urls_key, old_req.get_req_hash())

    async def deliver_result(self, result):
        result_out = {
            'id': self.task.get('id'),
            'value': result,
            'exporter_id': self.task.get('exporter_id'),
            'exporter_cfg': self.task.get('exporter_cfg')
        }
        if not self.has_ret_log:
            result_out['log'] = {
                'generator': {
                    'plugin_id': self.generator_id,
                    'state': self.g_log_state,
                    'content': self.g_log_stream.getvalue(),
                    'occur_time': self.g_log_time
                },
                'matcher': {
                    'plugin_id': self.matcher_id,
                    'state': self.m_log_state,
                    'content': self.m_log_stream.getvalue(),
                    'occur_time': self.m_log_time
                }
            }
            self.g_log_stream.close()
            self.m_log_stream.close()
            self.has_ret_log = True
        log.info('Result %s', result_out)
        await self.producer_send(self.result_topic_name, result_out)

    async def deliver_results(self, results):
        for result in results:
            await self.deliver_result(result)

    async def wait_to_get_executable(self, req_interval):
        # 简单分布式锁
        dlock_key = 'spider_last_time'
        while True:
            has_dlock = await self.redis.set(dlock_key, time(), nx=True, ex=req_interval)
            log.info('Has distributed lock %s', has_dlock)
            if has_dlock:
                break
            else:
                last_time = await self.redis.get(dlock_key)
                log.info('The last time %s', last_time)
                if last_time:
                    last_time = float(last_time.decode())
                    wait_time = last_time + req_interval - time()
                    if wait_time > 0:
                        await asyncio.sleep(wait_time)

    async def get_data(self):
        log.info('URL = %s', self.req.url)
        timeout = self.timeout
        if 'timeout' in self.task:
            timeout = self.task.get('timeout')
        if 'req_interval' in self.task:
            req_interval = self.task.get('req_interval')
            if req_interval > 0:
                await self.wait_to_get_executable(req_interval)
        log.info('Method %s', self.req.method)
        log.info('Headers %s', self.req.headers)
        log.info('Timeout %s', timeout)
        log.info('Payload %s', self.req.payload)
        async with self.session.request(self.req.method, self.req.url, timeout=timeout, headers=self.req.headers, data=self.req.payload) as resp:
            self.resp = Response(self.req.url, resp.headers, await resp.read())
            self.task['last_time'] = time()

    async def get_robots(self):
        self.use_robots = self.task.get('use_robots')
        if not self.use_robots:
            self.use_robots = False
            return
        try:
            self.robot_parser = AIORobotFileParser()
            m = self.re_match_site.match(self.req.url)
            if m:
                robot_url = '{}/robots.txt'.format(m.group().strip('/'))
                log.info('Robot url %s', robot_url)
                self.robot_parser.set_url(robot_url)
                await self.robot_parser.read()
                log.info('Crawl delay %s', self.robot_parser.crawl_delay('*'))
                log.info('Request rate %s',
                         self.robot_parser.request_rate('*'))
            else:
                self.robot_parser = None
        except:
            self.robot_parser = None

    async def create_tasks(self):
        generator_id = self.task.get('generator_id')
        if not generator_id:
            return
        if self.generator_id != generator_id:
            self.generator_id = generator_id
            await self.get_generator()
        self.generator.log = logging.getLogger(self.generator_id)
        self.generator.log.setLevel(logging.DEBUG)
        self.g_log_stream = StringIO()
        for h in self.generator.log.handlers:
            self.generator.log.removeHandler(h)
        self.generator.log.addHandler(logging.StreamHandler(self.g_log_stream))
        generator_cfg = self.task.get('generator_cfg')
        if generator_cfg:
            self.generator_cfg = generator_cfg
        if not self.generator_cfg:
            self.generator_cfg = dict()
        log.info('Generator %s', self.generator)
        try:
            self.g_log_time = time()
            next_reqs, old_reqs = await self.generator.generate(self.generator_cfg, self.req, self.resp)
            log.info('Next urls %s', next_reqs)
        except Exception as e:
            self.generator.log.error(e, exc_info=True)
            self.g_log_state = 1
            log.error(e, exc_info=True)
            next_reqs = None
            old_reqs = None
        if next_reqs:
            await self.publish_tasks(next_reqs)
            self.next_reqs = next_reqs
        if old_reqs:
            await self.add_old_urls(old_reqs)

    async def sync_task_state(self):
        await self.task_lock.acquire(blocking=True, blocking_timeout=30)
        try:
            ds_task_key = 'lanxuage_ds_task_info_' + str(self.task.get('id'))
            ds_task = await self.redis.get(ds_task_key)
            log.info('DS task %s', ds_task)
            if ds_task and ds_task != b'null':
                ds_task = json.loads(ds_task)
                log.info('Next reqs %s', self.next_reqs)
                if self.next_reqs:
                    ds_task['total_reqs'] += len(self.next_reqs)
                log.info('Results %s', self.results)
                if self.results:
                    ds_task['total_results'] += len(self.results)
                ds_task['reqs_processed'] += 1
                await self.redis.set(ds_task_key, json.dumps(ds_task).encode())
        except Exception as e:
            log.error(e, exc_info=True)
        await self.task_lock.release()
        self.next_reqs = None
        self.results = None

    async def get_generator(self):
        generator_code_bin = await self.redis.get(self.generator_id)
        self.generator = await self.get_component('generator', generator_code_bin)

    async def get_component(self, component_type, c_code_bin):
        c_code = marshal.loads(zstd.uncompress(c_code_bin))
        c_module = types.ModuleType(component_type)
        exec(c_code, c_module.__dict__)
        return c_module

    async def get_matcher(self):
        matcher_code_bin = await self.redis.get(self.matcher_id)
        self.matcher = await self.get_component('matcher', matcher_code_bin)

    async def create_results(self):
        matcher_id = self.task.get('matcher_id')
        if not matcher_id:
            return
        if self.matcher_id != matcher_id:
            self.matcher_id = matcher_id
            await self.get_matcher()
            log.info('Got matcher')
        self.matcher.log = logging.getLogger(self.matcher_id)
        self.matcher.log.setLevel(logging.DEBUG)
        self.m_log_stream = StringIO()
        for h in self.matcher.log.handlers:
            self.matcher.log.removeHandler(h)
        self.matcher.log.addHandler(logging.StreamHandler(self.m_log_stream))
        matcher_cfg = self.task.get('matcher_cfg')
        if matcher_cfg:
            self.matcher_cfg = matcher_cfg
        if not self.matcher_cfg:
            self.matcher_cfg = dict()
        try:
            self.m_log_time = time()
            results = await self.matcher.match(self.matcher_cfg, self.req, self.resp)
        except Exception as e:
            self.matcher.log.error(e, exc_info=True)
            self.m_log_state = 1
            log.error(e, exc_info=True)
            results = None
        if results:
            await self.deliver_results(results)
            self.results = results

    async def is_valid_task(self, task):
        return {'id', 'url', 'generator_id', 'generator_cfg', 'matcher_id', 'matcher_cfg', 'exporter_id', 'exporter_cfg'} <= task.keys()

    async def is_invalid_task(self):
        if not await self.is_valid_task(self.task):
            return True
        url = self.task.get('url')
        if not is_url(url):
            return True
        headers = self.headers
        if 'headers' in self.task:
            headers = self.task.get('headers')
            headers.update(self.headers)
        payload = None
        if 'payload' in self.task:
            payload = base64.b64decode(self.task.get('payload'))
        self.req = Request(url, self.task.get('method'), headers, payload)
        log.info('URL = %s. ', self.req.url)
        # if (await self.redis.sismember(self.old_urls_key, self.req.get_req_hash())):
        #    return True
        await self.get_robots()
        return self.use_robots and self.robot_parser and not self.robot_parser.can_fetch('*', self.req.url)

    async def close(self):
        await self.session.close()

    async def working(self):
        log.info('Start working')
        while True:
            try:
                await self.get_task()
                log.info('Got task %s', self.task)
                if (await self.is_invalid_task()):
                    log.info('Is invalid task. ')
                    continue
                await self.get_data()
                log.info('Got data')
                await self.create_tasks()
                log.info('Created tasks')
                await self.create_results()
                log.info('Created results')
                await self.sync_task_state()
                if self.stop:
                    break
            except Exception as e:
                log.error(e, exc_info=True)
