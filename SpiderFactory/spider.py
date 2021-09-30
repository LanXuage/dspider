#!/bin/env python3
# -*- coding: utf-8 -*-
import aiohttp
import asyncio
import imp
import json
import marshal

from urllib.parse import urlparse
from helpers import preprocess_url
from aiorobotparser import AIORobotFileParser

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47'
}

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
            headers=headers
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
        self.result = {}
        self.stop = False
        self.use_robots = False
        self.generator_id = None

    async def get_task(self):
        self.msg = await self.consumer.__anext__()
        self.task = json.loads(self.msg.value)

    async def publish_task(self, task):
        print(task)
        await self.producer.send_and_wait(self.task_topic_name, json.dumps(task).encode())

    async def publish_tasks(self, tasks):
        for task in tasks:
            await self.publish_task(task)

    async def deliver_result(self):
        await self.producer.send_and_wait(self.result_topic_name, json.dumps(self.result).encode())

    async def get_data(self):
        async with self.session.get(self.url, timeout=self.timeout, headers=self.headers) as resp:
            self.resp_raw = await resp.read()

    async def get_robots(self):
        self.use_robots = self.task.get('use_robots')
        if not self.use_robots:
            return
        self.robot_parser = AIORobotFileParser()
        self.robot_parser.set_url('{}://{}/robots.txt'.format(self.scheme, self.netloc))
        await self.robot_parser.read()

    async def create_tasks(self):
        generator_id = self.task.get('generator')
        if not generator_id:
            return
        if self.generator_id != generator_id:
            self.generator_id = generator_id
            await self.get_generator()
        try:
            tasks = await self.generator(self.url, self.resp_raw)
        except:
            tasks = set()
        if not tasks:
            return
        await self.publish_tasks(tasks)

    async def get_generator(self):
        generator_code_bin = await self.redis.get(self.generator_id)
        generator_code = marshal.loads(generator_code_bin)
        generator_moudle = imp.new_module('generator')
        exec(generator_code, generator_moudle.__dict__)
        self.generator = generator_moudle.generate

    async def create_result(self):
        pass

    async def is_invalid_task(self):
        url = self.task.get('url')
        if not url:
            return True
        url = preprocess_url(url)
        #if (await self.redis.sismember(self.old_urls_key, url)):
        #    return True
        await self.redis.sadd(self.old_urls_key, url)
        self.url = url
        url_parse = urlparse(self.url)
        if url_parse.scheme:
            self.scheme = url_parse.scheme
        else:
            self.scheme = 'http'
        self.netloc = url_parse.netloc
        return False

    async def working(self):
        print('working')
        while True:
            await self.get_task()
            print(self.task)
            if (await self.is_invalid_task()):
                continue
            await self.get_robots()
            await self.get_data()
            tasks = await self.create_tasks()
            if self.stop:
                break
    
