#!/bin/bash

# Ожидание запуска Postgres
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "Postgres недоступен, жду..."
  sleep 2
done

echo "Postgres запущен, выполняю миграции..."
python manage.py makemigrations
python manage.py migrate

# Проверяем наличие данных в базе данных вместо файла
echo "Проверяю наличие данных в базе..."

# Проверяем обычные тесты и вопросы (app)
TESTS_COUNT=$(python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ent_trainer.settings')
django.setup()
try:
    from app.models import Test
    print(Test.objects.count())
except Exception as e:
    print('0')
" 2>/dev/null || echo "0")

QUESTIONS_COUNT=$(python -c "
import django
import os  
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ent_trainer.settings')
django.setup()
try:
    from app.models import Question
    print(Question.objects.count())
except Exception as e:
    print('0')
" 2>/dev/null || echo "0")

# Проверяем материалы (learning_materials)
SECTIONS_COUNT=$(python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ent_trainer.settings')
django.setup()
try:
    from learning_materials.models import Section
    print(Section.objects.count())
except Exception as e:
    print('0')
" 2>/dev/null || echo "0")

MATERIALS_COUNT=$(python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ent_trainer.settings')
django.setup()
try:
    from learning_materials.models import Material
    print(Material.objects.count())
except Exception as e:
    print('0')
" 2>/dev/null || echo "0")

# Проверяем контекстные вопросы (context_questions)
CONTEXT_SETS_COUNT=$(python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ent_trainer.settings')
django.setup()
try:
    from context_questions.models import ContextQuestionSet
    print(ContextQuestionSet.objects.count())
except Exception as e:
    print('0')
" 2>/dev/null || echo "0")

CONTEXT_QUESTIONS_COUNT=$(python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ent_trainer.settings')
django.setup()
try:
    from context_questions.models import Question
    print(Question.objects.count())
except Exception as e:
    print('0')
" 2>/dev/null || echo "0")

echo "Найдено в базе:"
echo "  Тесты: $TESTS_COUNT"
echo "  Вопросы: $QUESTIONS_COUNT"
echo "  Секции материалов: $SECTIONS_COUNT"
echo "  Материалы: $MATERIALS_COUNT"
echo "  Контекстные наборы: $CONTEXT_SETS_COUNT"
echo "  Контекстные вопросы: $CONTEXT_QUESTIONS_COUNT"

# Импортируем обычные тесты и вопросы, если их нет
if [ "$TESTS_COUNT" -eq "0" ] || [ "$QUESTIONS_COUNT" -eq "0" ]; then
  echo "Импортирую обычные тесты и вопросы..."
  python manage.py import_json
  echo "Импорт обычных тестов завершен."
else
  echo "Обычные тесты уже есть в базе (Тестов: $TESTS_COUNT, Вопросов: $QUESTIONS_COUNT), пропускаю."
fi

# Импортируем материалы, если их нет
if [ "$SECTIONS_COUNT" -eq "0" ] || [ "$MATERIALS_COUNT" -eq "0" ]; then
  echo "Импортирую материалы..."
  python manage.py import_materials
  echo "Импорт материалов завершен."
else
  echo "Материалы уже есть в базе (Секций: $SECTIONS_COUNT, Материалов: $MATERIALS_COUNT), пропускаю."
fi

# Импортируем контекстные вопросы, если их нет
if [ "$CONTEXT_SETS_COUNT" -eq "0" ] || [ "$CONTEXT_QUESTIONS_COUNT" -eq "0" ]; then
  echo "Импортирую контекстные вопросы..."
  python manage.py import_context_questions
  echo "Импорт контекстных вопросов завершен."
else
  echo "Контекстные вопросы уже есть в базе (Наборов: $CONTEXT_SETS_COUNT, Вопросов: $CONTEXT_QUESTIONS_COUNT), пропускаю."
fi

echo "Все импорты завершены. Запускаю сервер..."
exec python manage.py runserver 0.0.0.0:8000