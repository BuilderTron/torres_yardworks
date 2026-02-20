#!/bin/sh
set -e

# Copy collected static files into the volume (ensures updates on redeploy)
if [ -d /app/staticfiles_build ]; then
    cp -r /app/staticfiles_build/. /app/static/
fi

# Run database migrations
python manage.py migrate --noinput

exec "$@"
