#!/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import asyncio

from aiokafka import AIOKafkaProducer
from config import KAFKA_SERVERS, RESULT_TOPIC_NAME, SASL_MECHANISM, SASL_PLAIN_USERNAME, SASL_PLAIN_PASSWORD, SECURITY_PROTOCOL, SSL_CONTEXT, KAFKA_VERSION, COMPRESSION_TYPE

log = logging.getLogger(__name__)


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
        jizhile_result = {'username': 'gh_406cd9af657e', 'nickname': '北京新闻', 'aliasname': 'brtvbjxw', 'register_body': '北京广播电视台', 'signature': '聚焦北京的新闻，着力报道热点民生；关心北京的事儿，时常发布实用信息；专注北京的生活，不断发放大小福利。无论是否身在北京，您需要来自北京的新闻！',
                          'head_img': 'http://mmbiz.qpic.cn/mmbiz_png/LCChw9N6UicdRoeibDg82mPebcm46nq9ian3CpoDHLsqLKajT6uNyC7UyuibwzQZpjNA377IqInO1bthpGsnzAuCJA/0?wx_fmt=png', 'doc_id': '3079855037', 'type': 'wechat_oaccount', 'appid': ''}
        jizhile_result_out = {
            'id': 1,
            'value': jizhile_result
        }
        await producer.send_and_wait(RESULT_TOPIC_NAME, json.dumps(jizhile_result_out).encode())
        log.info('Publish result done. ')
    finally:
        await producer.stop()

asyncio.run(send())
