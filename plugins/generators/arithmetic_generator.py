#!/bin/env python3
import re
import json
import base64
import asyncio

from common.net import Request, Response

# type : url | headers | payload
# re_an_1 : 正则，用于匹配前一项, base64
# re_an_1_group : int, 前一项匹配中后的组ID
# d : int, 公差
# match : 正则, base64
# replace : 替换被match匹配到的部分，可使用{{an}}来插入当前项的值, base64


async def generate(cfg: dict, req: Request, resp: Response):
    log.info(resp.raw) # log 由运行环境注入
    t = cfg.get('type')
    if t == 'url':
        next_url = get_next(cfg, req.url.encode())
        if not next_url:
            return [], [req]
        return [Request(next_url, req.method, req.headers, req.payload)], [req]
    elif t == 'headers':
        next_headers = get_next(cfg, json.dumps(req.headers).encode())
        if not next_headers:
            return [], [req]
        return [Request(req.url, req.method, json.loads(next_headers), req.payload)], [req]
    elif t == 'payload':
        next_payload = get_next(cfg, req.payload)
        if not next_payload:
            return [], [req]
        return [Request(req.url, req.method, req.headers, next_payload)], [req]
    return [], [req]


def get_next(cfg, data):
    m = re.search(base64.b64decode(cfg.get('re_an_1')), data)
    if not m:
        return None
    an_1 = int(m.group(cfg.get('re_an_1_group')))
    an = an_1 + cfg.get('d')
    replace_s = base64.b64decode(cfg.get('replace')).decode().replace(
        '{{an}}', str(an)).encode()
    return re.sub(base64.b64decode(cfg.get('match')), replace_s, data)


if __name__ == '__main__':
    payload = {"kw": "北京广播电视台", "page": 1, "num": 10, "extra": 0, "area": "", "dajiala_index": "", "fans": "", "filter_kw": "", "industries": "0,",
               "kw_type": "2", "publish_total": "", "recent": "", "register": "", "st": "", "top_praise": "", "top_read": "", "type": "", "zhuti": ""}
    req = Request(url="https://www.jzl.com/fbmain/search/v1/senior_search/name",
                  method='POST', payload=json.dumps(payload).encode())
    print(req.payload)
    cfg = {'type': 'payload', 're_an_1': base64.b64encode('"page":\s*(\d+),'.encode()).decode(), 're_an_1_group': 1, 'd': 1, 'match': base64.b64encode(
        '"page":\s*(\d+),'.encode()).decode(), 'replace': base64.b64encode('"page": {{an}},'.encode()).decode()}
    print(json.dumps(cfg))
    next_reqs, _ = asyncio.run(generate(cfg, req, None))
    print(next_reqs[0].payload)
