#!/bin/bash 
docker compose down
docker compose up --build -d 

# Swarm
#docker stack rm mystack && docker stop $(docker ps -q) 
#docker stack deploy -c docker-compose.yml mystack
