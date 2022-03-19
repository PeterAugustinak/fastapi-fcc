#!/bin/bash
docker-compose up -d
sudo chmod -R 755 ../var/pgdata/pgdata/
docker exec -it postgres-personal bash -c "psql -U postgres"
