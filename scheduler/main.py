#!/bin/env python3
from kafka import KafkaProducer

from config import KAFKA_SERVERS, SSL_CHECK_HOSTNAME, SASL_MECHANISM, SASL_PLAIN_USERNAME, SASL_PLAIN_PASSWORD, SECURITY_PROTOCOL, SSL_CAFILE, SSL_CERTFILE, SSL_KEYFILE, KAFKA_VERSION

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVERS,
    ssl_check_hostname=SSL_CHECK_HOSTNAME,
    sasl_mechanism=SASL_MECHANISM,
    sasl_plain_username=SASL_PLAIN_USERNAME,
    sasl_plain_password=SASL_PLAIN_PASSWORD,
    security_protocol=SECURITY_PROTOCOL,
    ssl_cafile=SSL_CAFILE,
    ssl_certfile=SSL_CERTFILE,
    ssl_keyfile=SSL_KEYFILE,
    api_version=KAFKA_VERSION
)
producer.send('dspider', b'some_message_bytes')
