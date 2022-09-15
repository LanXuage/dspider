#!/bin/env python3
# -*- coding: utf-8 -*-
import aiohttp

from urllib import robotparser


class AIORobotFileParser(robotparser.RobotFileParser):
    async def read(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                if resp.status in (401, 403):
                    self.disallow_all = True
                elif resp.status >= 400 and resp.status < 500:
                    self.allow_all = True
                raw = await resp.read()
                self.parse(raw.decode("utf-8").splitlines())
