#!/bin/env python3
import asyncio
import logging
import asyncpg
import aioredis

from aiokafka import AIOKafkaProducer
from config import KAFKA_SERVERS, SASL_MECHANISM, SASL_PLAIN_USERNAME, SASL_PLAIN_PASSWORD, SECURITY_PROTOCOL, TASK_TOPIC_NAME, KAFKA_VERSION, COMPRESSION_TYPE, SSL_CONTEXT, PG_DNAME, PG_UNAME, PG_PASSWD, PG_HOST, PG_PORT, REDIS_URL, REDIS_USERNAME, REDIS_PASSWORD
from task_processor_unit import TaskProcessorUnit

log = logging.getLogger(__name__)


class TaskProcessor:
    def __init__(self, num_unit=1):
        self.num_unit = num_unit
        self.pg_pool = None
        self.producer = None
        self.redis = None

    async def get_producer(self):
        log.info('Geting Producer. ')
        if not self.producer:
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

    async def get_redis(self):
        if not self.redis:
            self.redis = await aioredis.from_url(
                REDIS_URL,
                username=REDIS_USERNAME,
                password=REDIS_PASSWORD
            )

    async def get_pg_pool(self):
        if not self.pg_pool:
            self.pg_pool = await asyncpg.create_pool(database=PG_DNAME, user=PG_UNAME, password=PG_PASSWD, host=PG_HOST, port=PG_PORT)

    async def run(self):
        try:
            log.info('Task Processor start. ')
            await self.get_producer()
            await self.get_redis()
            await self.get_pg_pool()
            self.units = []
            self.unit_coroutines = []
            for _ in range(self.num_unit):
                unit = TaskProcessorUnit(
                    self.producer,
                    self.redis,
                    self.pg_pool,
                    TASK_TOPIC_NAME,
                )
                self.units.append(unit)
                self.unit_coroutines.append(unit.processing())
            await asyncio.gather(*self.unit_coroutines, return_exceptions=True)
        except asyncio.exceptions.CancelledError as e:
            await self.close()
            raise e
        except Exception as e:
            log.error(e, exc_info=True)

    async def close(self):
        log.info('Closing. ')
        await self.producer.close()


if __name__ == '__main__':
    tprocessor = TaskProcessor()
    asyncio.run(tprocessor.run())
