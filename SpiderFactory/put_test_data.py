#!/bin/env python3
import json
import logging
import asyncio

from aiokafka import AIOKafkaProducer
from aiokafka.helpers import create_ssl_context
from config import KAFKA_SERVERS, SSL_CHECK_HOSTNAME, SASL_MECHANISM, SASL_PLAIN_USERNAME, SASL_PLAIN_PASSWORD, SECURITY_PROTOCOL, SSL_CAFILE, KAFKA_VERSION, TASK_TOPIC_NAME, COMPRESSION_TYPE

logging.basicConfig(level=logging.DEBUG)

async def send():
    ssl_context = create_ssl_context(cafile=SSL_CAFILE)
    ssl_context.check_hostname = SSL_CHECK_HOSTNAME
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_SERVERS,
        sasl_mechanism=SASL_MECHANISM,
        sasl_plain_username=SASL_PLAIN_USERNAME,
        sasl_plain_password=SASL_PLAIN_PASSWORD,
        security_protocol=SECURITY_PROTOCOL,
        ssl_context=ssl_context,
        api_version=KAFKA_VERSION,
        compression_type=COMPRESSION_TYPE
    )
    await producer.start()
    try:
        task = {
            "id": 1,
            "url": "https://www.baidu.com/index.php",
            "use_robots": True,
            "matcher": "matcher_uuid",
            "generator": "generator_uuid"
        }
        await producer.send_and_wait(TASK_TOPIC_NAME, json.dumps(task).encode())
    finally:
        await producer.stop()

asyncio.run(send())



