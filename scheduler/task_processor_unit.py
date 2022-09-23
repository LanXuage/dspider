#!/bin/env python3
import zstd
import json
import base64
import asyncio
import logging
import marshal
import platform

from asyncpg import Pool, exceptions
from aioredis import Redis
from croniter import croniter
from crc import Crc64, CrcCalculator
from aiokafka import AIOKafkaProducer
from datetime import datetime, timedelta

log = logging.getLogger(__name__)


class TaskProcessorUnit:
    def __init__(self, producer: AIOKafkaProducer, redis: Redis, pg_pool: Pool, task_topic_name: str):
        self.task_topic_name = task_topic_name
        self.producer = producer
        self.redis = redis
        self.pg_pool = pg_pool
        self.stop = False
        self.task_lock = None
        self.crc64 = CrcCalculator(Crc64.CRC64)
        self.start_time = None
        self.task_id = None

    def gen_task_id(self, plan_id):
        return '{:0>16s}'.format(hex(self.crc64.calculate_checksum(
            (str(self.start_time.timestamp()) + '_' + str(plan_id)).encode()))[2:])

    async def is_need_to_run(self, plan):
        current_time = datetime.now().astimezone()
        plan_status = plan.get('plan_status')
        if plan_status != 1:
            return False
        if plan.get('is_periodic'):
            cron_expn = plan.get('cron_expn')
            iter = croniter(cron_expn, current_time - timedelta(minutes=1))
            self.start_time = iter.get_next(datetime)
            self.task_id = self.gen_task_id(plan.get('id'))
            if (not await self.has_task()) and self.start_time <= (current_time - timedelta(seconds=2)):
                return True
        else:
            self.start_time = plan.get('start_time').astimezone()
            self.task_id = self.gen_task_id(plan.get('id'))
            if (not await self.has_task()) and self.start_time <= (current_time + timedelta(seconds=2)):
                return True
        self.task_id = None
        self.start_time = None
        return False

    async def has_task(self):
        async with self.pg_pool.acquire() as conn:
            tasks = await conn.fetch(
                'SELECT 1 FROM ds_task WHERE id = $1', self.task_id)
            if len(tasks) > 0:
                return True
        return False

    async def get_plans(self):
        async with self.pg_pool.acquire() as conn:
            return await conn.fetch('SELECT * FROM ds_plan')

    async def create_task(self, plan):
        t = datetime.now().astimezone()
        try:
            async with self.pg_pool.acquire() as conn:
                await conn.execute('INSERT INTO ds_task (id, task_status, start_time, update_time, create_time, reqs_processed, results_processed, total_reqs, total_results, plan_id) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)',
                                   self.task_id, 0, self.start_time, t, t, 0, 0, 1, 0, plan.get('id'))
                tasks = await conn.fetch(
                    'SELECT * FROM ds_task WHERE id = $1', self.task_id)
                if len(tasks) == 1:
                    return tasks[0]
        except exceptions.UniqueViolationError:
            pass
        except Exception as e:
            log.error(e, exc_info=True)
        return

    async def publish_task(self, plan):
        unnecessary_keys = ['user_id', 'is_periodic', 'plan_status', 'cron_expn',
                            'start_time', 'update_time', 'create_time', 'plan_name']
        need_json_decode_keys = [
            'headers', 'generator_cfg', 'matcher_cfg', 'exporter_cfg']
        need_base64_encode_keys = ['payload']
        for k in list(plan.keys()):
            if k in unnecessary_keys:
                del plan[k]
            elif k in need_json_decode_keys:
                plan[k] = json.loads(plan.get(k))
            elif k in need_base64_encode_keys:
                plan[k] = base64.b64encode(plan.get(k)).decode()
        plan['id'] = self.task_id
        log.info('Publish task: %s', plan)
        await self.producer.send_and_wait(self.task_topic_name, zstd.compress(json.dumps(plan).encode(), 18))

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
                    await conn.execute('UPDATE ds_plugin SET code_obj = $1, code_obj_version = $2, update_time = $3 WHERE id = $4',
                                       code_raw, current_version, datetime.now().astimezone(), plugin_id)
                    return code_raw
        return None

    async def cache_plugin_to_redis(self, plan):
        plugin_keys = ['generator_id', 'matcher_id', 'exporter_id']
        for k in plugin_keys:
            plugin_id = plan.get(k)
            code_raw = await self.get_plugin_code(plugin_id)
            await self.redis.set(plugin_id, code_raw)

    async def init_task_state(self, task):
        unnecessary_keys = ['start_time', 'update_time', 'create_time', 'end_time', 'plan_id']
        for k in list(task.keys()):
            if isinstance(task.get(k), datetime) or k in unnecessary_keys:
                del task[k]
        await self.task_lock.acquire(blocking=True, blocking_timeout=30)
        try:
            ds_task_key = 'lanxuage_ds_task_info_' + str(task.get('id'))
            await self.redis.set(ds_task_key, json.dumps(task).encode())
        except Exception as e:
            log.error(e, exc_info=True)
        await self.task_lock.release()

    async def processing(self):
        while True:
            try:
                if self.stop:
                    break
                plans = await self.get_plans()
                for plan in plans:
                    if await self.is_need_to_run(plan):
                        log.info('Need to run. ')
                        # 采用乐观锁，只有创建成功才算拿到任务。
                        task = await self.create_task(plan)
                        if task:
                            if self.task_lock:
                                try:
                                    await self.task_lock.release()
                                except:
                                    pass
                            self.task_lock = self.redis.lock(
                                'lanxuage_ds_task_lock_' + str(task.get('id')))
                            await self.cache_plugin_to_redis(plan)
                            await self.publish_task(dict(plan))
                            await self.init_task_state(dict(task))
                await asyncio.sleep(5)
                log.info('Check DS tasks. ')
            except Exception as e:
                log.error(e, exc_info=True)
