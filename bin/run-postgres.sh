#!/bin/bash
docker-compose up -d
docker exec -it postgres-personal bash -c "psql -U postgres"


