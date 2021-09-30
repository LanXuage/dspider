#!/bin/env python3

# ip:port 格式，多个使用,隔开
KAFKA_SERVERS = '127.0.0.1:9092'
# 是否检查证书域名合法性
SSL_CHECK_HOSTNAME = False

SASL_MECHANISM = 'PLAIN'

SASL_PLAIN_USERNAME = 'dspider'

SASL_PLAIN_PASSWORD = 'f916743824a64ed4ae15633825ebd577'

SECURITY_PROTOCOL = 'SASL_SSL'

SSL_CAFILE = './pem/caroot.pem'

SSL_CERTFILE = './pem/cert.pem'

SSL_KEYFILE = './pem/key.pem'

KAFKA_VERSION = (2,8,1)

TASK_TOPIC_NAME = 'dspiderTask'

RESULT_TOPIC_NAME = 'dspiderResult'
