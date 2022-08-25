#!/bin/sh
docker-compose down
rm -rf bitnami/kafka/*
rm -rf bitnami/zookeeper/*
rm -rf bitnami/redis/*
docker-compose up -d
