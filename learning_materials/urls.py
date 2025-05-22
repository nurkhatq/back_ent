# learning_materials/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SectionViewSet, MaterialViewSet

router = DefaultRouter()
router.register(r'sections', SectionViewSet)
router.register(r'materials', MaterialViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

