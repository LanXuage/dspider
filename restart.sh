#!/bin/sh
docker-compose down
rm -rf data/kafka
rm -rf data/zookeeper
rm -rf data/redis
docker-compose up -d
