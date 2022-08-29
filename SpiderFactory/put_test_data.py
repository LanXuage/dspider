#!/bin/env python3
# -*- coding: utf-8 -*-
import base64
import json
import logging
import asyncio

from aiokafka import AIOKafkaProducer
from config import KAFKA_SERVERS, SASL_MECHANISM, SASL_PLAIN_USERNAME, SASL_PLAIN_PASSWORD, SECURITY_PROTOCOL, SSL_CONTEXT, KAFKA_VERSION, TASK_TOPIC_NAME, COMPRESSION_TYPE

log = logging.getLogger(__name__)

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
payload = {"kw": "北京广播电视台","page":1,"num":10,"extra":0,"area":"","dajiala_index":"","fans":"","filter_kw":"","industries":"0,","kw_type":"2","publish_total":"","recent":"","register":"","st":"","top_praise":"","top_read":"","type":"","zhuti":""}

async def send():
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_SERVERS,
        sasl_mechanism=SASL_MECHANISM,
        sasl_plain_username=SASL_PLAIN_USERNAME,
        sasl_plain_password=SASL_PLAIN_PASSWORD,
        security_protocol=SECURITY_PROTOCOL,
        ssl_context=SSL_CONTEXT,
        api_version=KAFKA_VERSION,
        compression_type=COMPRESSION_TYPE
    )
    await producer.start()
    try:
        task = {
            "id": 1, # required
            "url": "https://www.baidu.com/index.php", # required
            "method": "GET",
            "headers": "{\"token\":\"123456\"}",
            "payload": "e30=", # encode with base64
            "timeout": 60,
            "use_robots": True,
            "use_tor": False,
            "use_proxy": False,
            "matcher": "matcher_id", # required
            "matcher_cfg": "{}",
            "generator": "generator_id", # required
            "generator_cfg": "{}",
            "exporter": "exporter_id",
            "exporter_cfg": "{}",
            "is_periodic": False,
            "task_status": 0, # 0 未开始，1 执行中，2 已结束
            "cron_expn": "0 */4 * * *",
            "req_interval": 15, # 单位s
            "start_time": "2022-08-23 16:50", # must with timezone
            "update_time": "2022-08-23 16:35",
            "create_time": "2022-08-23 16:35"
        }
        jizhile_task = {
            "id": 2,
            "url": "https://www.jzl.com/fbmain/search/v1/senior_search/name",
            "method": "POST",
            "headers": json.dumps(headers),
            "payload": base64.b64encode(json.dumps(payload).encode()).decode(),
            "matcher": "json",
            "matcher_cfg": '{"type": "more", "map": {"username": "qrcode:username=(gh_.*?)([^a-z0-9]|$):1", "nickname": "mp_name", "aliasname": "wxid", "register_body": "zhuti", "signature": "desc", "head_img": "avatar:fileb64e", "doc_id": "biz:b64d"}, "item": "data.accounts", "add": {"type": "wechat_oaccount", "appid": ""}}',
            "generator": "arithmetic",
            "generator_cfg": '{"type": "payload", "re_an_1": "InBhZ2UiOlxzKihcZCspLA==", "re_an_1_group": 1, "d": 1, "match": "InBhZ2UiOlxzKihcZCspLA==", "replace": "InBhZ2UiOiB7e2FufX0s"}',
            "req_interval": 15,
        }
        await producer.send_and_wait(TASK_TOPIC_NAME, json.dumps(jizhile_task).encode())
        log.info('Publish task done. ')
    finally:
        await producer.stop()

asyncio.run(send())



