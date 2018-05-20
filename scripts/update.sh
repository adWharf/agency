#!/usr/bin/env bash
docker stop agency || true
docker rm -v agency || true
docker build -t agency .
docker run -p 5000:5000 --rm --name agency --restart=always -dagency
