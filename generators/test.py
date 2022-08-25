#!/bin/env python3
#-*- coding: utf-8 -*-
import asyncio

async def generate(url, payload, raw):
    print(url)
    await asyncio.sleep(0)
    print(raw)
    return {{'url': 'url', 'method': 'GET', 'headers': '{"key":"value"}'}}, {"old_url"}

