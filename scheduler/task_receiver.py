#!/bin/env python3
import logging
import asyncio
import asyncpg
import aioredis

from aiokafka import AIOKafkaConsumer
from connects_mgr import ConnectsManger
from task_receiver_unit import TaskReceiverUnit
from config import KAFKA_SERVERS, SASL_MECHANISM, SASL_PLAIN_USERNAME, SASL_PLAIN_PASSWORD, SECURITY_PROTOCOL, KAFKA_VERSION, RESULT_TOPIC_NAME, SSL_CONTEXT, GROUP_ID, REDIS_URL, REDIS_USERNAME, REDIS_PASSWORD, PG_HOST, PG_DNAME, PG_PASSWD, PG_PORT, PG_UNAME

log = logging.getLogger(__name__)


class TaskReceiver:
    def __init__(self, num_unit=1):
        self.num_unit = num_unit
        self.pg_pool = None
        self.conn_mgr = None
        self.consumer = None
        self.redis = None

    async def get_redis(self):
        if not self.redis:
            self.redis = await aioredis.from_url(
                REDIS_URL,
                username=REDIS_USERNAME,
                password=REDIS_PASSWORD
            )

    async def get_consumer(self):
        if not self.consumer:
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

    async def get_pg_pool(self):
        if not self.pg_pool:
            self.pg_pool = await asyncpg.create_pool(database=PG_DNAME, user=PG_UNAME, password=PG_PASSWD, host=PG_HOST, port=PG_PORT)

    async def get_conn_mgr(self):
        if not self.conn_mgr:
            self.conn_mgr = ConnectsManger()
            await self.conn_mgr.start()

    async def run(self):
        try:
            await self.get_consumer()
            await self.get_redis()
            await self.get_pg_pool()
            await self.get_conn_mgr()
            self.units = []
            self.unit_coroutines = []
            for _ in range(self.num_unit):
                unit = TaskReceiverUnit(
                    self.consumer,
                    self.redis,
                    self.pg_pool,
                    self.conn_mgr
                )
                self.units.append(unit)
                self.unit_coroutines.append(unit.receivering())
            await asyncio.gather(*self.unit_coroutines, return_exceptions=True)
        except asyncio.exceptions.CancelledError as e:
            await self.close()
            raise e
        except Exception as e:
            log.error(e, exc_info=True)

    async def close(self):
        await self.consumer.stop()


if __name__ == '__main__':
    task_receiver = TaskReceiver()
    asyncio.run(task_receiver.run())
