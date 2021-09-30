#!/bin/env python3
# -*- coding: utf-8 -*-
import aioredis
import asyncio

from spider import Spider
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from config import KAFKA_SERVERS, SASL_MECHANISM, SASL_PLAIN_USERNAME, SASL_PLAIN_PASSWORD, SECURITY_PROTOCOL, KAFKA_VERSION, TASK_TOPIC_NAME, RESULT_TOPIC_NAME, COMPRESSION_TYPE, SSL_CONTEXT, GROUP_ID, REDIS_URL, REDIS_USERNAME, REDIS_PASSWORD, OLD_URLS_KEY


class Workshop:
    def __init__(self, num_spiders=3):
        self.num_spiders = 3
        self.stop = False

    async def get_redis(self):
        self.redis = await aioredis.from_url(
            REDIS_URL,
            username=REDIS_USERNAME, 
            password=REDIS_PASSWORD
        )

    async def get_producer(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_SERVERS,
            sasl_mechanism=SASL_MECHANISM,
            sasl_plain_username=SASL_PLAIN_USERNAME,
            sasl_plain_password=SASL_PLAIN_PASSWORD,
            security_protocol=SECURITY_PROTOCOL,
            ssl_context=SSL_CONTEXT,
            api_version=KAFKA_VERSION,
            compression_type=COMPRESSION_TYPE
        )
        await self.producer.start()

    async def get_consumer(self):
        self.consumer = AIOKafkaConsumer(
            TASK_TOPIC_NAME,
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

    async def run(self):
        await self.get_redis()
        await self.get_producer()
        await self.get_consumer()
        print(self.redis)
        print(self.producer)
        print(self.consumer)
        self.spiders = []
        self.spider_coroutines= []
        for _ in range(self.num_spiders):
            spider = Spider(
                self.consumer, 
                self.producer, 
                self.redis, 
                TASK_TOPIC_NAME, 
                RESULT_TOPIC_NAME, 
                OLD_URLS_KEY
            ) 
            self.spiders.append(spider)
            self.spider_coroutines.append(spider.working())
        asyncio.gather(*self.spider_coroutines)
        while True:
            await asyncio.sleep(1)
            if self.stop:
                break
        await self.close()

    async def close(self):
        await self.producer.stop()
        await self.consumer.stop()
        await self.redis.close()


if __name__ == '__main__':
    workshop = Workshop()
    asyncio.run(workshop.run())
