#!/bin/env python3
# -*- coding: utf-8 -*-
import base64
from datetime import datetime
import json
import logging
import asyncio
import asyncpg

from aiokafka import AIOKafkaProducer
from config import KAFKA_SERVERS, SASL_MECHANISM, SASL_PLAIN_USERNAME, SASL_PLAIN_PASSWORD, SECURITY_PROTOCOL, SSL_CONTEXT, KAFKA_VERSION, TASK_TOPIC_NAME, COMPRESSION_TYPE

log = logging.getLogger(__name__)

task = {
    "id": 1,  # required
    "url": "https://www.baidu.com/index.php",  # required
    "method": "GET",
    "headers": "{\"token\":\"123456\"}",
    "payload": "e30=",  # encode with base64
    "timeout": 60,
    "use_robots": True,
    "use_tor": False,
    "use_proxy": False,
    "matcher": "matcher_id",  # required
    "matcher_cfg": "{}",
    "generator": "generator_id",  # required
    "generator_cfg": "{}",
    "exporter": "exporter_id",
    "exporter_cfg": "{}",
    "is_periodic": False,
    "task_status": 0,  # 0 未开始，1 执行中，2 已结束
    "cron_expn": "0 */4 * * *",
    "req_interval": 15,  # 单位s
    "start_time": "2022-08-23 16:50",  # must with timezone
    "update_time": "2022-08-23 16:35",
    "create_time": "2022-08-23 16:35"
}


access_token = '21861_da40243437434b644174a6544172e879'

headers = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62',
    'Origin': 'https://www.dajiala.com',
    'Content-Type': 'application/json',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'accessToken': access_token,
    'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Accept': 'application/json, text/plain, */*',
    'Connection': 'close'
}
payload = {"kw": "北京广播电视台", "page": 1, "num": 10, "extra": 0, "area": "", "dajiala_index": "", "fans": "", "filter_kw": "", "industries": "0,",
           "kw_type": "2", "publish_total": "", "recent": "", "register": "", "st": "", "top_praise": "", "top_read": "", "type": "", "zhuti": ""}


async def send():
    matcher_cfg = {"type": "more", "map": {"username": "qrcode:username=(gh_.*?)([^a-z0-9]|$):1", "nickname": "mp_name", "aliasname": "wxid", "register_body": "zhuti",
                                           "signature": "desc", "head_img": "avatar:fileb64e", "doc_id": "biz:b64d"}, "item": "data.accounts", "add": {"type": "wechat_oaccount", "appid": ""}}
    generator_cfg = {"type": "payload", "re_an_1": "InBhZ2UiOlxzKihcZCspLA==", "re_an_1_group": 1,
                     "d": 1, "match": "InBhZ2UiOlxzKihcZCspLA==", "replace": "InBhZ2UiOiB7e2FufX0s"}
    jizhile_task = {
        "id": 1,
        "user_id": 1,
        "url": "https://www.jzl.com/fbmain/search/v1/senior_search/name",
        "method": "POST",
        "headers": headers,
        "payload": json.dumps(payload).encode(),
        "timeout": 30,
        "use_robots": False,
        "use_tor": False,
        "use_proxy": False,
        "generator_id": "d906ec4c9228aeb3",
        "generator_cfg": generator_cfg,
        "matcher_id": "370997ab9656a5ee",
        "matcher_cfg": matcher_cfg,
        "exporter_id": "b9bccef6cd18f7db",
        "exporter_cfg": {},
        "is_periodic": False,
        "task_status": 0,
        "req_interval": 15,
        "start_time": datetime.now().astimezone(),
        "update_time": datetime.now().astimezone(),
        "create_time": datetime.now().astimezone(),
        "task_name": "jizhile"
    }
    conn = await asyncpg.connect(database='dspider', user='postgres', password='7URL8rCIbJNNKq', host='127.0.0.1', port='65432')
    await conn.execute('INSERT INTO ds_task (id, user_id, url, method, headers, payload, timeout, use_robots, use_tor, use_proxy, generator_id, generator_cfg, matcher_id, matcher_cfg, exporter_id, exporter_cfg, \
        is_periodic, task_status, req_interval, start_time, update_time, create_time, task_name) \
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23)',
                       jizhile_task['id'], jizhile_task['user_id'], jizhile_task['url'], jizhile_task['method'], json.dumps(jizhile_task['headers']), jizhile_task['payload'], 
                       jizhile_task['timeout'], jizhile_task['use_robots'], jizhile_task['use_tor'], jizhile_task['use_proxy'], jizhile_task['generator_id'], json.dumps(jizhile_task['generator_cfg']), 
                       jizhile_task['matcher_id'], json.dumps(jizhile_task['matcher_cfg']), jizhile_task['exporter_id'], json.dumps(jizhile_task['exporter_cfg']), jizhile_task['is_periodic'], 
                       jizhile_task['task_status'], jizhile_task['req_interval'], jizhile_task['start_time'], jizhile_task['update_time'], jizhile_task['create_time'], 
                       jizhile_task['task_name'])
    await conn.close()
    log.info('Publish task done. ')

asyncio.run(send())
