#!/bin/bash

# Configuration
DB_NAME="masque_et_la_plume"          
BACKUP_DIR="/home/guillaume/git/lmelp/db/masque_et_la_plume/"   

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Create a date string for the backup folder
DATE=$(date +%Y-%m-%d_%H-%M-%S)

# Run mongodump
mongodump --db "$DB_NAME" --out "${BACKUP_DIR}/backup_${DATE}"

if [ $? -eq 0 ]; then
    echo "Backup successful: ${BACKUP_DIR}/backup_${DATE}"
else
    echo "Backup failed."
fi