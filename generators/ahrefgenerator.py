#!/bin/env python3
#-*- coding: utf-8 -*-
import asyncio

from bs4 import BeautifulSoup

async def generate(url, raw):
    tasks = set()
    soup = BeautifulSoup(raw, 'lxml')
    for a in soup.findAll('a'):
        if a.has_attr('href'):
            tasks.add(a['href'])
    return tasks

