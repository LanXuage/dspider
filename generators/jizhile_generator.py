#!/bin/env python3
#-*- coding: utf-8 -*-
import json

async def generate(url, payload, raw):
    print(raw)
    new_payload = json.loads(payload)
    new_payload['page'] = new_payload['page'] + 1
    next_url = {'url': url, 'method': 'POST', 'payload': new_payload}
    next_urls = [next_url]
    return next_urls, set()
