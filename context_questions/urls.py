# context_questions/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContextQuestionSetViewSet

router = DefaultRouter()
router.register(r'question-sets', ContextQuestionSetViewSet)

urlpatterns = [
    path('', include(router.urls)),
]