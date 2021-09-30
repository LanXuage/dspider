#!/bin/env python3
#-*- coding: utf-8 -*-
from aiokafka.helpers import create_ssl_context

### Kafka 配置 ###
# ip:port 格式，多个使用,隔开
KAFKA_SERVERS = 'localhost:9093'
# 是否检查证书域名合法性
SSL_CHECK_HOSTNAME = False

SASL_MECHANISM = 'PLAIN'

SASL_PLAIN_USERNAME = 'dspider'

SASL_PLAIN_PASSWORD = 'f916743824a64ed4ae15633825ebd577'

SECURITY_PROTOCOL = 'SASL_SSL'

SSL_CAFILE = './pem/CARoot.pem'

KAFKA_VERSION = '2.8.1'

TASK_TOPIC_NAME = 'dspiderTask'

RESULT_TOPIC_NAME = 'dspiderResult'

COMPRESSION_TYPE = 'gzip'

GROUP_ID = 'spiders'

SSL_CONTEXT = create_ssl_context(cafile=SSL_CAFILE)
SSL_CONTEXT.check_hostname = SSL_CHECK_HOSTNAME

### Redis 配置 ###
REDIS_URL = 'redis://localhost:6379'

REDIS_USERNAME = 'default'

REDIS_PASSWORD = 'c08c2813cf7747818225aff03300aba0'

OLD_URLS_KEY = 'oldUrlsKey'
