#!/bin/env python3
#-*- coding: utf-8 -*-
# 安全方面涉及python沙箱逃逸问题
from bs4 import BeautifulSoup
from urllib.parse import urlparse

async def generate(url, payload, raw):
    old_urls = set()
    old_urls.add(url)
    next_urls = set()
    soup = BeautifulSoup(raw, 'lxml')
    for a in soup.findAll('a'):
        if a.has_attr('href'):
            next_url = a['href']
            if next_url.startswith('/'):
                up = urlparse(url)
                next_url = up.scheme + '://' + up.netloc + next_url
            next_urls.add({'url': next_url})
    return next_urls, old_urls

