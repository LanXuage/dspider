#!/bin/env python3
#-*- coding: utf-8 -*-
from urllib.parse import urlparse, parse_qs

def preprocess_url(url):
    up = urlparse(url)
    old_queries = parse_qs(up.query)
    if not old_queries:
        return '{}://{}{}'.format(up.scheme, up.netloc, up.path)
    new_query = ''
    for i in sorted(old_querys.keys()):
        for j in old_querys.get(i):
            new_query += '{}={}&'.format(i, j)
    if not new_query:
        return '{}://{}{}'.format(up.scheme, up.netloc, up.path)
    return '{}://{}{}?{}'.format(up.scheme, up.netloc, up.path, new_query[:-1])

