#!/usr/bin/env bash
set -euo pipefail

docker build -t cookie-agent:latest ./agent

docker stack deploy -c docker-compose.yml yourstack
