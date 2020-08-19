#!/bin/sh
set -e

if [ "$1" = 'manage.py' ]; then
  echo "Starting server..."
  ./manage.py migrate
  ./manage.py collectstatic --noinput
  exec /usr/local/bin/gunicorn arapheno.wsgi:application -w 9 --max-requests 1000 --max-requests-jitter 50 --timeout 300 -b :8000
fi
echo "Runing command..."
exec "$@"
