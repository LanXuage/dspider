#!/bin/env python3

import asyncio
from time import time


class ConnectsManger:
    def __init__(self, max_conn=10, check_interval=120):
        self.conns = dict()
        self.times = dict()
        self.max_conn = max_conn
        self.check_interval = check_interval

    async def put(self, key, conn):
        t = time()
        self.conns[t] = conn
        self.times[key] = t

    async def get(self, key):
        t = self.times.get(key)
        if not t:
            return None
        return self.conns.get(t)

    async def start(self):
        asyncio.create_task(self.check_loop())

    async def check_loop(self):
        while True:
            try:
                await asyncio.sleep(self.check_interval)
                await self.check()
            except:
                pass

    async def check(self):
        if len(self.conns) > self.max_conn:
            keys = []
            for t in sorted(self.conns.keys())[:-10]:
                for k in self.times.keys():
                    if self.times.get(k) == t:
                        keys.append(k)
            for k in keys:
                try:
                    self.times[k].close()
                except Exception as e:
                    pass
                del self.times[k]
