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
    with open('generators/ahrefgenerator.py', 'rb') as f:
        code = compile(f.read(), filename='ahrefgenerator.py', mode='exec')
        await redis.set('generator_id', marshal.dumps(code))
        await redis.close()
    with open('generators/arithmetic_generator.py', 'rb') as f:
        code = compile(f.read(), filename='arithmetic_generator.py', mode='exec')
        await redis.set('arithmetic', marshal.dumps(code))
        await redis.close()

asyncio.run(main())
