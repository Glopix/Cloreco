#!/usr/bin/env bash
REPO="ghcr.io/glopix/cloreco"

docker build -t "${REPO}/cloreco-frontend" --target frontend .
docker build -t "${REPO}/cloreco-backend"  --target backend  .

docker push "${REPO}/cloreco-frontend"
docker push "${REPO}/cloreco-backend"