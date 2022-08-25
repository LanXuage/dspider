#!/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import asyncio

from aiokafka import AIOKafkaProducer
from config import KAFKA_SERVERS, SASL_MECHANISM, SASL_PLAIN_USERNAME, SASL_PLAIN_PASSWORD, SECURITY_PROTOCOL, SSL_CONTEXT, KAFKA_VERSION, TASK_TOPIC_NAME, COMPRESSION_TYPE

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
        task = {
            "id": 1, # required
            "url": "https://www.baidu.com/index.php", # required
            "use_robots": True,
            "use_tor": False,
            "use_proxy": False,
            "matcher": "matcher_id", # required
            "generator": "generator_id", # required
            "exporter": "exporter_id", # required
            "is_periodic": False,
            "task_status": 0, # 0 未开始，1 执行中，2 已结束
            "cron_expn": "* */4 * * *",
            "start_time": "2022-08-23 16:50", # must with timezone
            "update_time": "2022-08-23 16:35",
            "create_time": "2022-08-23 16:35"
        }
        await producer.send_and_wait(TASK_TOPIC_NAME, json.dumps(task).encode())
        log.info('Publish task done. ')
    finally:
        await producer.stop()

asyncio.run(send())



