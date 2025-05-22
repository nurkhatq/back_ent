# context_questions/apps.py
from django.apps import AppConfig

class ContextQuestionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'context_questions'
    verbose_name = 'Context Questions'