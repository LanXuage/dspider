#!/bin/env python3
# -*- coding: utf-8 -*-
# 安全方面涉及python沙箱逃逸问题
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from common.net import Request, Response


async def generate(cfg: dict, req: Request, resp: Response):
    next_reqs = []
    soup = BeautifulSoup(resp.raw, 'lxml')
    for a in soup.findAll('a'):
        if a.has_attr('href'):
            next_url = a['href']
            if next_url.startswith('/'):
                up = urlparse(req.url)
                next_url = up.scheme + '://' + up.netloc + next_url
            next_reqs.append(Request(next_url))
    return next_reqs, [req]
