#!/bin/env python3
# -*- coding: utf-8 -*-
import imp
import json
import asyncio
import marshal
import aioredis

from aiokafka import AIOKafkaConsumer
from config import KAFKA_SERVERS, SASL_MECHANISM, SASL_PLAIN_USERNAME, SASL_PLAIN_PASSWORD, SECURITY_PROTOCOL, KAFKA_VERSION, RESULT_TOPIC_NAME, SSL_CONTEXT, GROUP_ID, REDIS_URL, REDIS_USERNAME, REDIS_PASSWORD


class TaskReceiver:
    def __init__(self, num_task_receiver_async=1, api=None):
        self.api = api
        if self.api:
            self.use_api = True
        else:
            self.use_api = False
        self.receiverings = [self.receivering() for _ in range(num_task_receiver_async)]
        self.stop = False
        self.exporter = None
        self.exporter_id = None

    async def get_redis(self):
        self.redis = await aioredis.from_url(
            REDIS_URL,
            username=REDIS_USERNAME, 
            password=REDIS_PASSWORD
        )

    async def get_consumer(self):
        self.consumer = AIOKafkaConsumer(
            RESULT_TOPIC_NAME,
            bootstrap_servers=KAFKA_SERVERS,
            security_protocol=SECURITY_PROTOCOL,
            sasl_mechanism=SASL_MECHANISM,
            sasl_plain_username=SASL_PLAIN_USERNAME,
            sasl_plain_password=SASL_PLAIN_PASSWORD,
            ssl_context=SSL_CONTEXT,
            api_version=KAFKA_VERSION,
            group_id=GROUP_ID
        )
        await self.consumer.start()

    async def get_component(self, component_type, c_code_bin):
        c_code = marshal.loads(c_code_bin)
        c_module = imp.new_module(component_type)
        exec(c_code, c_module.__dict__)
        return c_module

    async def get_exporter(self):
        exporter_code_bin = await self.redis.get(self.exporter_id)
        self.exporter = await self.get_component('exporter', exporter_code_bin)
    
    async def export_result(self, result):
        task_id = result.get('id')
        if self.use_api:
            exporter_id = await self.get_exporter_id_from_api(task_id)
        else:
            exporter_id = await self.get_exporter_id_from_db(task_id)
        if not exporter_id:
            return None
        if self.exporter_id != exporter_id:
            self.exporter_id = exporter_id
            await self.get_exporter()
        try:
            await self.exporter.export(result)
        except:
            pass
    
    async def receivering(self):
        while True:
            if self.stop:
                break
            result_raw = await self.consumer.__anext__()
            result = json.loads(result_raw.value)
            await self.export_result(result)
    
    async def run(self):
        await self.get_consumer()
        asyncio.gather(*self.receiverings)
        while True:
            await asyncio.sleep(1)
            if self.stop:
                break
        await self.close()
    
    async def close(self):
        await self.consumer.stop()


if __name__ == '__main__':
    task_receiver = TaskReceiver()
    asyncio.run(task_receiver.run())