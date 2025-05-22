# app/apps.py
from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    
    def ready(self):
        # Этот метод выполняется при запуске приложения
        # Пропускаем создание записей во время миграции или создания таблиц
        import sys
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
            
        # Импортируем здесь, чтобы избежать циклических импортов
        from app.models import Test
        
        # Используем try-except, чтобы избежать ошибок при отсутствии таблицы
        try:
            # Создаем специальный тест для пробного ЕНТ, если его еще нет
            if not Test.objects.filter(id=9999).exists():
                Test.objects.create(
                    id=9999,
                    title="Пробный ЕНТ (Случайные вопросы)",
                    total_questions=40,
                    multiple_answers_allowed=True,
                    has_images=True
                )
        except Exception as e:
            # Логируем ошибку вместо падения приложения
            print(f"Error creating test with ID 9999: {str(e)}")