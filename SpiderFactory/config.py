#!/bin/env python3
# -*- coding: utf-8 -*-
import logging

from aiokafka.helpers import create_ssl_context


logging.basicConfig(level=logging.INFO)
### Kafka 配置 ###
# ip:port 格式，多个使用,隔开
KAFKA_SERVERS = 'kafka:9093'
# 是否检查证书域名合法性
SSL_CHECK_HOSTNAME = False

SASL_MECHANISM = 'PLAIN'

SASL_PLAIN_USERNAME = 'dspider'

SASL_PLAIN_PASSWORD = 'agheLahb0eij'

SECURITY_PROTOCOL = 'SASL_SSL'

SSL_CAFILE = 'certs/caroot.pem'
SSL_CERTFILE = 'certs/cert-signed.pem'
SSL_KEYFILE = 'certs/cert.key'
SSL_CONTEXT = create_ssl_context(
    cafile=SSL_CAFILE, certfile=SSL_CERTFILE, keyfile=SSL_KEYFILE)
SSL_CONTEXT.check_hostname = SSL_CHECK_HOSTNAME

KAFKA_VERSION = '2.8.1'

TASK_TOPIC_NAME = 'dspiderTask'

RESULT_TOPIC_NAME = 'dspiderResult'

COMPRESSION_TYPE = 'gzip'

GROUP_ID = 'spiders'

### Redis 配置 ###
REDIS_URL = 'redis://redis:6379'

REDIS_USERNAME = 'default'

REDIS_PASSWORD = 'Vah7ahWae1Ke'

OLD_URLS_KEY = 'oldUrlsKey'
