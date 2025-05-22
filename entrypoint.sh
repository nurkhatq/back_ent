#!/bin/bash

# Ожидание запуска Postgres
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "Postgres недоступен, жду..."
  sleep 2
done

echo "Postgres запущен, выполняю миграции..."
python manage.py makemigrations
python manage.py migrate

# Проверяем, нужно ли выполнять импорт данных
# Создаем файл-флаг после первого импорта
if [ ! -f "/code/.import_done" ]; then
  echo "Первый запуск - импортирую данные..."
  python manage.py import_json
  python manage.py import_materials
  python manage.py import_context_questions
  
  # Создаем флаг, что импорт выполнен
  touch /code/.import_done
  echo "Импорт данных завершен."
else
  echo "Импорт данных пропущен (уже был выполнен ранее)."
  echo "Для повторного импорта используйте: docker-compose run web python manage.py [import_json/import_materials/import_context_questions]"
fi

echo "Запускаю сервер..."
exec python manage.py runserver 0.0.0.0:8000