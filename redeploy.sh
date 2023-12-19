#!/bin/bash
docker build . -t quaxly 
docker-compose down --remove-orphans
docker-compose up -d
