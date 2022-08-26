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
    with open('matchers/test.py', 'rb') as f:
        code = compile(f.read(), filename='test.py', mode='exec')
        await redis.set('matcher_id', marshal.dumps(code))
        await redis.close()
    with open('matchers/json_matcher.py', 'rb') as f:
        code = compile(f.read(), filename='json_matcher.py', mode='exec')
        await redis.set('json', marshal.dumps(code))
        await redis.close()

asyncio.run(main())
