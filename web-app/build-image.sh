#!/usr/bin/env bash
REPO="ghcr.io/glopix/abcd"

docker build -t "${REPO}/abcd-frontend" --target frontend .
docker build -t "${REPO}/abcd-backend"  --target backend  .

docker push "${REPO}/abcd-frontend"
docker push "${REPO}/abcd-backend"