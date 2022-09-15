#!/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

from common.net import Request, Response


async def match(cfg: dict, req: Request, resp: Response):
    print(req.url)
    await asyncio.sleep(0)
    print(resp.raw)
    return []
