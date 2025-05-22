# app/urls.py (обновите существующие URLs или создайте файл)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestViewSet, TestResultViewSet, ContextTestResultViewSet

router = DefaultRouter()
router.register(r'tests', TestViewSet)
router.register(r'test-results', TestResultViewSet)
router.register(r'context-test-results', ContextTestResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
]