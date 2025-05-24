# !/bin/sh

# python manage.py flush --no-input
# python manage.py migrate
python manage.py collectstatic --no-input
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@email.com')" | python manage.py shell
gunicorn app.wsgi:application --bind 0.0.0.0:3001
exec "$@"