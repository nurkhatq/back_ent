# learning_materials/serializers.py (исправленная версия)
from rest_framework import serializers
from .models import Section, Material, MaterialImage

class MaterialImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = MaterialImage
        fields = ['id', 'image', 'caption', 'order']

    def get_image(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url
        return None

class MaterialSerializer(serializers.ModelSerializer):
    images = MaterialImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Material
        fields = [
            'id', 'title', 'content_html', 'original_file', 
            'has_images', 'has_tables', 'has_formulas', 
            'created_at', 'images'
        ]

class SectionSerializer(serializers.ModelSerializer):
    materials = MaterialSerializer(many=True, read_only=True)
    
    class Meta:
        model = Section
        fields = ['id', 'number', 'title', 'materials']