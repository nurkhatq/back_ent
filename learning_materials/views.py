# learning_materials/views.py (исправленная версия)
import mimetypes
import os
from django.http import Http404, HttpResponse
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from ent_trainer import settings
from .models import Section, Material
from .serializers import SectionSerializer, MaterialSerializer

class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Section.objects.all().prefetch_related('materials')
    serializer_class = SectionSerializer
    permission_classes = [AllowAny]

class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Material.objects.all().prefetch_related('images')
    serializer_class = MaterialSerializer
    permission_classes = [AllowAny]
