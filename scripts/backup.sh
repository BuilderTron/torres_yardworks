#!/bin/bash
# backup.sh — Daily backup of SQLite database and media files
# Designed to run via cron on the Droplet:
#   0 3 * * * /opt/torres-yardworks/scripts/backup.sh >> /var/log/torres-backup.log 2>&1
#
# The script runs the SQLite backup INSIDE the web container (via docker compose exec)
# and tars media from the named Docker volume on the host.

set -euo pipefail

PROJECT_DIR="/opt/torres-yardworks"
BACKUP_DIR="/opt/torres-yardworks/backups"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo "=== Backup started at $(date) ==="

# Ensure backup directory exists
mkdir -p "${BACKUP_DIR}"

# --- SQLite online backup (safe, non-locking) ---
echo "Backing up SQLite database..."
docker compose -f "${PROJECT_DIR}/compose.prod.yaml" exec -T web \
    python3 -c "
import sqlite3, sys
src = sqlite3.connect('/app/data/db.sqlite3')
dst = sqlite3.connect('/app/data/db-backup-${TIMESTAMP}.sqlite3')
src.backup(dst)
dst.close()
src.close()
print('SQLite backup completed inside container.')
"

# Copy the backup file out of the container
docker compose -f "${PROJECT_DIR}/compose.prod.yaml" cp \
    web:/app/data/db-backup-${TIMESTAMP}.sqlite3 \
    "${BACKUP_DIR}/db-${TIMESTAMP}.sqlite3"

# Remove the temporary backup file from inside the container
docker compose -f "${PROJECT_DIR}/compose.prod.yaml" exec -T web \
    rm -f /app/data/db-backup-${TIMESTAMP}.sqlite3

echo "Database backup saved to ${BACKUP_DIR}/db-${TIMESTAMP}.sqlite3"

# --- Media backup ---
echo "Backing up media files..."
MEDIA_VOLUME=$(docker volume ls --format '{{.Name}}' | grep -E 'torres.*media' | head -1)

if [ -n "${MEDIA_VOLUME}" ]; then
    docker run --rm \
        -v "${MEDIA_VOLUME}:/media:ro" \
        -v "${BACKUP_DIR}:/backups" \
        alpine:3 \
        tar czf "/backups/media-${TIMESTAMP}.tar.gz" -C /media .
    echo "Media backup saved to ${BACKUP_DIR}/media-${TIMESTAMP}.tar.gz"
else
    echo "WARNING: Could not find media volume, skipping media backup."
fi

# --- Prune old backups ---
echo "Pruning backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -name "db-*.sqlite3" -mtime +${RETENTION_DAYS} -delete
find "${BACKUP_DIR}" -name "media-*.tar.gz" -mtime +${RETENTION_DAYS} -delete

echo "=== Backup completed at $(date) ==="
