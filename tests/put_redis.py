#!/bin/env python3
import marshal
import aioredis
import asyncio

from config import REDIS_URL, REDIS_USERNAME, REDIS_PASSWORD 

async def main():
    redis = await aioredis.from_url(
        REDIS_URL,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD
    )
    with open('matchers/json_matcher.py', 'rb') as f:
        code = compile(f.read(), filename='json_matcher.py', mode='exec')
        await redis.set('json', marshal.dumps(code))
        await redis.close()
    with open('generators/ahrefgenerator.py', 'rb') as f:
        code = compile(f.read(), filename='ahrefgenerator.py', mode='exec')
        await redis.set('ahref', marshal.dumps(code))
        await redis.close()
    with open('generators/arithmetic_generator.py', 'rb') as f:
        code = compile(f.read(), filename='arithmetic_generator.py', mode='exec')
        await redis.set('arithmetic', marshal.dumps(code))
        await redis.close()
    with open('exporters/pg_exporter.py', 'rb') as f:
        code = compile(f.read(), filename='pg_exporter.py', mode='exec')
        await redis.set('pg', marshal.dumps(code))
        await redis.close()

asyncio.run(main())
