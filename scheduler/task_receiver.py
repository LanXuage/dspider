#!/bin/env python3
import json
import types
import logging
import asyncio
import asyncpg
import marshal
import aioredis

from aiokafka import AIOKafkaConsumer
from config import KAFKA_SERVERS, SASL_MECHANISM, SASL_PLAIN_USERNAME, SASL_PLAIN_PASSWORD, SECURITY_PROTOCOL, KAFKA_VERSION, RESULT_TOPIC_NAME, SSL_CONTEXT, GROUP_ID, REDIS_URL, REDIS_USERNAME, REDIS_PASSWORD
from connects_mgr import ConnectsManger

log = logging.getLogger(__name__)


class TaskReceiver:
    def __init__(self, num_task_receiver_async=1, api=None):
        self.api = api
        if self.api:
            self.use_api = True
        else:
            self.use_api = False
        self.tasks = [self.receivering()
                      for _ in range(num_task_receiver_async)]
        self.stop = False
        self.exporter = None
        self.exporter_id = None
        self.conn_mgr = ConnectsManger()
        self.tasks.append(self.conn_mgr.start())

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
        c_module = types.ModuleType(component_type)
        exec(c_code, c_module.__dict__)
        return c_module

    async def get_exporter(self):
        exporter_code_bin = await self.redis.get(self.exporter_id)
        self.exporter = await self.get_component('exporter', exporter_code_bin)

    async def gen_conn_id(self, task_id, exporter_id):
        return str(task_id) + ':' + str(exporter_id)

    async def gen_pgsql_conn(self, exporter_cfg):
        return await asyncpg.create_pool(database=exporter_cfg.get('dbname'), user=exporter_cfg.get('username'), password=exporter_cfg.get('password'), host=exporter_cfg.get('host'), port=exporter_cfg.get('port'))

    async def gen_mysql_conn(self, exporter_cfg):
        pass

    async def init_cfg(self, exporter_cfg, conn_id):
        t = exporter_cfg.get('type')
        if t == 'pgsql':
            conn = await self.conn_mgr.get(conn_id)
            if not conn:
                conn = await self.gen_pgsql_conn(exporter_cfg)
                await self.conn_mgr.put(conn_id, conn)
            exporter_cfg['conn'] = conn
        elif t == 'mysql':
            conn = await self.conn_mgr.get(conn_id)
            if not conn:
                conn = await self.gen_mysql_conn(exporter_cfg)
                await self.conn_mgr.put(conn_id, conn)
            exporter_cfg['conn'] = conn
        return exporter_cfg

    async def get_exporter_id_and_cfg_from_db(self, task_id):
        return 'pg', {
            'type': 'pgsql',
            'host': '127.0.0.1',
            'port': '65432',
            'username': 'postgres',
            'password': '7URL8rCIbJNNKq',
            'dbname': 'dstest',
            'unique_fields': ['username'],
            'table_name': 'vrp_oasa_data',
            'pkey_name': 'id'
        }

    async def get_exporter_id_and_cfg_from_api(self, task_id):
        return await self.get_exporter_id_and_cfg_from_db(task_id)

    async def export_result(self, result):
        task_id = result.get('id')
        if self.use_api:
            exporter_id, exporter_cfg = await self.get_exporter_id_and_cfg_from_api(task_id)
        else:
            exporter_id, exporter_cfg = await self.get_exporter_id_and_cfg_from_db(task_id)
        if not exporter_id:
            return None
        if self.exporter_id != exporter_id:
            self.exporter_id = exporter_id
            await self.get_exporter()
        exporter_cfg = await self.init_cfg(exporter_cfg, await self.gen_conn_id(task_id, exporter_id))
        try:
            await self.exporter.export(exporter_cfg, result.get('value'))
        except Exception as e:
            log.error(e, exc_info=True)

    async def receivering(self):
        while True:
            if self.stop:
                break
            try:
                result_raw = await self.consumer.__anext__()
                result = json.loads(result_raw.value)
                await self.export_result(result)
            except Exception as e:
                log.error(e, exc_info=True)

    async def run(self):
        await self.get_redis()
        await self.get_consumer()
        await asyncio.gather(*self.tasks)
        await self.close()

    async def close(self):
        await self.consumer.stop()


if __name__ == '__main__':
    task_receiver = TaskReceiver()
    asyncio.run(task_receiver.run())
