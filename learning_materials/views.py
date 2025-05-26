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



def serve_material_image(request, filename):
    """Обслуживает изображения материалов"""
    try:
        # Путь к файлу
        file_path = os.path.join(settings.MEDIA_ROOT, 'material_images', filename)
        
        # Проверяем, существует ли файл
        if not os.path.exists(file_path):
            raise Http404("Изображение не найдено")
        
        # Определяем тип контента
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Читаем и возвращаем файл
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
            
    except Exception as e:
        raise Http404("Ошибка при загрузке изображения")
