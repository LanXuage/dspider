#!/bin/env python3
import zstd
import json
import base64
import asyncio
import logging
import marshal
import platform
from croniter import croniter
from datetime import datetime, timedelta
from aiokafka import AIOKafkaProducer
from aioredis import Redis
from asyncpg import Pool

log = logging.getLogger(__name__)


class TaskProcessorUnit:
    def __init__(self, producer: AIOKafkaProducer, redis: Redis, pg_pool: Pool, task_topic_name: str):
        self.task_topic_name = task_topic_name
        self.producer = producer
        self.redis = redis
        self.pg_pool = pg_pool
        self.stop = False
        self.task_lock = None

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
        async with self.pg_pool.acquire() as conn:
            return await conn.fetch('SELECT * FROM ds_task')

    async def modify_task_status(self, task):
        async with self.pg_pool.acquire() as conn:
            if 'UPDATE 1' == await conn.execute('UPDATE ds_task SET task_status = $1, update_time = $2 WHERE id = $3 AND task_status = $4', 1, datetime.now().astimezone(), task.get('id'), 0):
                return True
        return False

    async def publish_task(self, task):
        unnecessary_keys = ['user_id', 'is_periodic', 'task_status', 'cron_expn',
                            'start_time', 'update_time', 'create_time', 'task_name']
        need_json_decode_keys = [
            'headers', 'generator_cfg', 'matcher_cfg', 'exporter_cfg']
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
        await self.producer.send_and_wait(self.task_topic_name, zstd.compress(json.dumps(task).encode(), 18))

    async def get_plugin_code(self, plugin_id):
        async with self.pg_pool.acquire() as conn:
            results = await conn.fetch('SELECT plugin_name, plugin_plain, code_obj, code_obj_version FROM ds_plugin WHERE id = $1', plugin_id)
            if len(results) > 0:
                result = results[0]
                current_version = platform.python_version()
                if current_version == result.get('code_obj_version'):
                    return result.get('code_obj')
                else:
                    plugin_plain_raw = result.get('plugin_plain').encode()
                    code = compile(plugin_plain_raw, filename=result.get(
                        'plugin_name'), mode='exec')
                    code_raw = zstd.compress(marshal.dumps(code), 18)
                    await conn.execute('UPDATE ds_plugin SET code_obj = $1, code_obj_version = $2, update_time = $3 WHERE id = $4', code_raw, current_version, datetime.now().astimezone(), plugin_id)
                    return code_raw
        return None

    async def cache_plugin_to_redis(self, task):
        plugin_keys = ['generator_id', 'matcher_id', 'exporter_id']
        for k in plugin_keys:
            plugin_id = task.get(k)
            code_raw = await self.get_plugin_code(plugin_id)
            await self.redis.set(plugin_id, code_raw)

    async def init_task_state(self, task_id):
        await self.task_lock.acquire(blocking=True, blocking_timeout=30)
        try:
            ds_task_key = 'lanxuage_ds_task_info_' + str(task_id)
            ds_task = {
                'id': task_id,
                'tasks': 1,
                'tasks_done': 0,
                'results': 0,
                'results_done': 0
            }
            await self.redis.set(ds_task_key, json.dumps(ds_task).encode())
        except Exception as e:
            log.error(e, exc_info=True)
        await self.task_lock.release()

    async def processing(self):
        while True:
            try:
                if self.stop:
                    break
                tasks = await self.get_tasks()
                for task in tasks:
                    if await self.is_need_to_run(task):
                        log.info('Need to run. ')
                        # 采用乐观锁，只有修改成功才算拿到任务。
                        if await self.modify_task_status(task):
                            if self.task_lock:
                                try:
                                    await self.task_lock.release()
                                except:
                                    pass
                            self.task_lock = self.redis.lock(
                                'lanxuage_ds_task_lock_' + str(task.get('id')))
                            await self.cache_plugin_to_redis(task)
                            await self.publish_task(dict(task))
                            await self.init_task_state(task.get('id'))
                log.info('Wait 30s')
                await asyncio.sleep(30)
            except Exception as e:
                log.error(e, exc_info=True)
