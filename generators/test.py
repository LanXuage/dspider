#!/bin/env python3
#-*- coding: utf-8 -*-
import asyncio

async def generate(url, raw):
    print(url)
    await asyncio.sleep(1)
    print(raw)

