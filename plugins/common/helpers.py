#!/bin/env python3
# -*- coding: utf-8 -*-
import re

from urllib.parse import urlparse, parse_qs

re_match_url = re.compile(r'^https?://[\w.-/]+$')


def preprocess_url(url):
    up = urlparse(url)
    old_queries = parse_qs(up.query)
    if not old_queries:
        return '{}://{}{}'.format(up.scheme, up.netloc, up.path)
    new_query = preprocess_dict(old_queries)
    if not new_query:
        return '{}://{}{}'.format(up.scheme, up.netloc, up.path)
    return '{}://{}{}?{}'.format(up.scheme, up.netloc, up.path, new_query)


def is_url(url):
    if re_match_url.match(url):
        return True
    else:
        return False


def preprocess_list_or_set(k, los):
    ret = ''
    for i in sorted(los):
        ret += '{}={}&'.format(k, i)
    return ret.strip('&')


def preprocess_dict(d):
    ret = ''
    for k in sorted(d.keys()):
        v = d.get(k)
        if isinstance(v, dict):
            v = k + '(' + preprocess_dict(v) + ')'
        elif isinstance(v, list):
            v = preprocess_list_or_set(k, v)
        elif isinstance(v, set):
            v = preprocess_list_or_set(k, v)
        else:
            v = '{}={}'.format(k, v)
        ret += v + '&'
    return ret.strip('&')


if __name__ == '__main__':
    print(preprocess_url('https://fanyi.baidu.com/?aldtype=16047&b=2233&b=1122'))
    print(preprocess_url('https://fanyi.baidu.com/?b=1122&b=2233&aldtype=16047'))
