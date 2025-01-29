#!/bin/bash
docker-compose build
docker-compose up -d
koii contract deploy SecureTACBridge
echo "Terminusa deployed at http://localhost:8080"