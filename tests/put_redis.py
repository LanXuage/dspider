#!/bin/env python3
import marshal
import aioredis
import asyncio
import asyncpg

from datetime import datetime
from crc import Crc64, CrcCalculator
from config import REDIS_URL, REDIS_USERNAME, REDIS_PASSWORD


async def set_plugin_to_redis(c, redis, fname):
    with open(fname, 'rb') as f:
        plugin_plain = f.read()
        code = compile(plugin_plain, filename=fname, mode='exec')
        code_bin = marshal.dumps(code)
        plugin_id = hex(c.calculate_checksum(code_bin))[2:]
        await redis.set(plugin_id, code_bin)
        return plugin_id, plugin_plain, code_bin


async def main():
    redis = await aioredis.from_url(
        REDIS_URL,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD
    )
    pg_conn = await asyncpg.connect(user='postgres', password='7URL8rCIbJNNKq', database='dspider', host='127.0.0.1', port=65432)
    c = CrcCalculator(Crc64.CRC64)
    fnames = ['matchers/json_matcher.py', 'generators/ahrefgenerator.py',
              'generators/arithmetic_generator.py', 'exporters/pg_exporter.py']
    for fname in fnames:
        plugin_id, plugin_plain, code_bin = await set_plugin_to_redis(c, redis, fname)
        plugin_type = 0 if fname.startswith('generators') else (
            1 if fname.startswith('matchers') else 2)
        plugin_plain = plugin_plain.decode()
        t = datetime.now().astimezone()
        async with pg_conn.transaction():
            await pg_conn.execute('INSERT INTO ds_plugin(id, plugin_name, plugin_type, plugin_plain, code_obj, update_time, create_time) VALUES($1, $2, $3, $4, $5, $6, $7)', plugin_id, fname, plugin_type, plugin_plain, code_bin, t, t)
    await redis.close()

asyncio.run(main())
