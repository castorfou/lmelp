#!/bin/bash
# Backup MongoDB database from lmelp container

set -e

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backup_${BACKUP_DATE}"

echo "Creating MongoDB backup..."
echo "Backup directory: $BACKUP_DIR"

# Create backup using mongodump
docker exec lmelp-mongodb mongodump \
    --db masque_et_la_plume \
    --out "/data/db/$BACKUP_DIR"

echo ""
echo "✅ Backup created successfully!"
echo ""
echo "The backup is stored inside the MongoDB container at:"
echo "/data/db/$BACKUP_DIR"
echo ""
echo "To copy it to your host machine, run:"
echo "docker cp lmelp-mongodb:/data/db/$BACKUP_DIR ./backup/"
