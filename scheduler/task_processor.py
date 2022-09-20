#!/bin/env python3
import base64
import json
import asyncio
import logging
import asyncpg

from croniter import croniter
from aiokafka import AIOKafkaProducer
from datetime import datetime, timedelta
from config import KAFKA_SERVERS, SASL_MECHANISM, SASL_PLAIN_USERNAME, SASL_PLAIN_PASSWORD, SECURITY_PROTOCOL, KAFKA_VERSION, TASK_TOPIC_NAME, COMPRESSION_TYPE, SSL_CONTEXT, PG_DNAME, PG_UNAME, PG_PASSWD, PG_HOST, PG_PORT

log = logging.getLogger(__name__)


class TaskProcessor:
    def __init__(self, nasync=1, api=None, m_api=None):
        self.stop = False
        self.api = api
        self.m_api = m_api
        if self.api and self.m_api:
            self.use_api = True
        else:
            self.use_api = False
        self.tasks = [
            self.processing() for _ in range(nasync)]
        self.pg_pool = None

    async def get_producer(self):
        log.info('Geting Producer. ')
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

    async def get_pg_pool(self):
        if not self.pg_pool:
            self.pg_pool = await asyncpg.create_pool(database=PG_DNAME, user=PG_UNAME, password=PG_PASSWD, host=PG_HOST, port=PG_PORT)

    async def get_tasks_from_db(self):
        await self.get_pg_pool()
        async with self.pg_pool.acquire() as conn:
            return await conn.fetch('SELECT * FROM ds_task')

    async def get_tasks_from_api(self):
        pass

    async def modify_task_status_to_api(self, task):
        return True

    async def modify_task_status_to_db(self, task):
        await self.get_pg_pool()
        async with self.pg_pool.acquire() as conn:
            if 'UPDATE 1' == await conn.execute('UPDATE ds_task SET task_status = $1 WHERE id = $2', 1, task.get('id')):
                return True
        return False

    async def is_need_to_run(self, task):
        current_time = datetime.now().astimezone()
        task_status = task.get('task_status')
        if task_status != 0:
            return False
        if task.get('is_periodic'):
            cron_expn = task.get('cron_expn')
            iter = croniter(cron_expn, current_time - timedelta(minutes=1))
            if iter.get_next(datetime) <= (current_time - timedelta(seconds=2)):
                return True
        else:
            start_time = task.get('start_time').astimezone()
            if start_time <= (current_time + timedelta(seconds=2)):
                return True
        return False

    async def get_tasks(self):
        if self.use_api:
            return await self.get_tasks_from_api()
        else:
            return await self.get_tasks_from_db()

    async def modify_task_status(self, task):
        if self.use_api:
            return await self.modify_task_status_to_api(task)
        else:
            return await self.modify_task_status_to_db(task)

    async def publish_task(self, task):
        unnecessary_keys = ['user_id', 'is_periodic', 'task_status', 'cron_expn',
                            'start_time', 'update_time', 'create_time', 'task_name']
        need_json_decode_keys = ['headers', 'generator_cfg', 'matcher_cfg', 'exporter_cfg']
        need_base64_encode_keys = ['payload']
        for k in list(task.keys()):
            if k in unnecessary_keys:
                del task[k]
            elif k in need_json_decode_keys:
                task[k] = json.loads(task.get(k))
            elif k in need_base64_encode_keys:
                task[k] = base64.b64encode(task.get(k)).decode()
        log.info('Publish task: %s', task)
        log.debug('Task len %s', len(json.dumps(task).encode()))
        await self.producer.send_and_wait(TASK_TOPIC_NAME, json.dumps(task).encode())

    async def processing(self):
        while True:
            if self.stop:
                break
            tasks = await self.get_tasks()
            for task in tasks:
                log.info('Processing %s', task)
                if await self.is_need_to_run(task):
                    log.info('Need to run. ')
                    # 采用乐观锁，只有修改成功才算拿到任务。
                    if await self.modify_task_status(task):
                        await self.publish_task(dict(task))
            await asyncio.sleep(30)

    async def run(self):
        log.info('Task Processor start. ')
        await self.get_producer()
        await asyncio.gather(*self.tasks)
        await self.close()

    async def close(self):
        log.info('Closing. ')
        await self.producer.close()
