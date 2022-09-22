#!/bin/env python3
import zstd
import json
import types
import asyncpg
import logging
import marshal
import aiomysql

from time import time
from io import StringIO
from aioredis import Redis
from datetime import datetime
from aiokafka import AIOKafkaConsumer

from connects_mgr import ConnectsManger

log = logging.getLogger(__name__)


class TaskReceiverUnit:
    def __init__(self, consumer: AIOKafkaConsumer, redis: Redis, pg_pool: asyncpg.pool, conn_mgr: ConnectsManger):
        self.stop = False
        self.exporter = None
        self.exporter_id = None
        self.e_log_state = 0
        self.consumer = consumer
        self.redis = redis
        self.pg_pool = pg_pool
        self.conn_mgr = conn_mgr
        self.task_lock = None

    async def get_component(self, component_type, c_code_bin):
        c_code = marshal.loads(zstd.uncompress(c_code_bin))
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
        return await aiomysql.create_pool(db=exporter_cfg.get('dbname'), user=exporter_cfg.get('username'), password=exporter_cfg.get('password'), host=exporter_cfg.get('host'), port=exporter_cfg.get('port'))

    async def init_cfg(self, exporter_cfg, conn_id):
        conn = await self.conn_mgr.get(conn_id)
        if not conn:
            t = exporter_cfg.get('type')
            if t == 'pgsql':
                conn = await self.gen_pgsql_conn(exporter_cfg)
            elif t == 'mysql':
                conn = await self.gen_mysql_conn(exporter_cfg)
            await self.conn_mgr.put(conn_id, conn)
        exporter_cfg['conn'] = conn
        return exporter_cfg

    async def export_result(self, result):
        task_id = result.get('id')
        exporter_id = result.get('exporter_id')
        exporter_cfg = result.get('exporter_cfg')
        if not exporter_id:
            return None
        if self.exporter_id != exporter_id:
            self.exporter_id = exporter_id
            await self.get_exporter()
        self.exporter.log = logging.getLogger(self.exporter_id)
        self.exporter.log.setLevel(logging.DEBUG)
        self.e_log_stream = StringIO()
        for h in self.exporter.log.handlers:
            self.exporter.log.removeHandler(h)
        self.exporter.log.addHandler(logging.StreamHandler(self.e_log_stream))
        try:
            self.e_log_time = time()
            exporter_cfg = await self.init_cfg(exporter_cfg, await self.gen_conn_id(task_id, exporter_id))
            await self.exporter.export(exporter_cfg, result.get('value'))
        except Exception as e:
            self.exporter.log.error(e, exc_info=True)
            self.e_log_state = 1
            log.error(e, exc_info=True)
        if 'log' not in result.keys():
            result['log'] = {}
        result['log']['exporter'] = {
            'plugin_id': self.exporter_id,
            'state': self.e_log_state,
            'content': self.e_log_stream.getvalue(),
            'occur_time': self.e_log_time
        }
        self.e_log_stream.close()
        await self.save_log(result)

    async def save_log(self, result):
        for ds_log in result.get('log').values():
            ds_log['task_id'] = result.get('id')
            ds_log['content'] = ds_log.get('content').encode()
            ds_log['create_time'] = datetime.now().astimezone()
            ds_log['occur_time'] = datetime.fromtimestamp(
                ds_log['occur_time']).astimezone()
            log.info(ds_log)
            async with self.pg_pool.acquire() as conn:
                log.info(await conn.execute('INSERT INTO ds_log (state, content, occur_time, create_time, plugin_id, task_id) VALUES ($1, $2, $3, $4, $5, $6)', ds_log.get('state'), ds_log.get('content'), ds_log.get('occur_time'), ds_log.get('create_time'), ds_log.get('plugin_id'), ds_log.get('task_id')))

    async def sync_task_state(self, result):
        await self.task_lock.acquire(blocking=True, blocking_timeout=30)
        try:
            ds_task_key = 'lanxuage_ds_task_info_' + str(result.get('id'))
            ds_task = await self.redis.get(ds_task_key)
            if ds_task and ds_task != b'null':
                ds_task = json.loads(ds_task)
                ds_task['results_done'] += 1
                await self.redis.set(ds_task_key, json.dumps(ds_task).encode())
        except Exception as e:
            log.error(e, exc_info=True)
        await self.task_lock.release()

    async def receivering(self):
        while True:
            if self.stop:
                break
            try:
                result_raw = await self.consumer.__anext__()
                result = json.loads(zstd.uncompress(result_raw.value))
                if self.task_lock:
                    try:
                        await self.task_lock.release()
                    except:
                        pass
                self.task_lock = self.redis.lock(
                    'lanxuage_ds_task_lock_' + str(result.get('id')))
                log.info(result)
                await self.export_result(result)
                await self.sync_task_state(result)
            except Exception as e:
                log.error(e, exc_info=True)
