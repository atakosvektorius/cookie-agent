#!/bin/bash 
docker stack rm mystack && docker stop $(docker ps -q) 
#docker stack deploy -c docker-compose.yml mystack
