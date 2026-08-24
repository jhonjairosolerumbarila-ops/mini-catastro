#!/bin/sh
set -e

echo ">> Aplicando migraciones..."
python manage.py migrate --noinput

echo ">> Creando superusuario (si no existe)..."
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    python manage.py createsuperuser --noinput 2>/dev/null \
        && echo "   Superusuario '$DJANGO_SUPERUSER_USERNAME' creado." \
        || echo "   Ya existia. Continuando."
fi

echo ">> Cargando datos de ejemplo..."
python manage.py loaddata fixtures/initial_data.json || true

echo ">> Backend listo en http://localhost:8000/"
exec "$@"
