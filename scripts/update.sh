#!/usr/bin/env bash
docker stop agency || true
docker rm -v agency || true
docker build -t agency .
docker run -p 5000:5000 --name agency --restart=always -d agency
