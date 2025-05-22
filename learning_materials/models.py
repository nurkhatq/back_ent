# # learning_materials/models.py
# from django.db import models

# class Section(models.Model):
#     """Main section of learning materials"""
#     number = models.IntegerField()
#     title = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ['number']

#     def __str__(self):
#         return f"{self.number}. {self.title}"

# class Material(models.Model):
#     """Learning material with HTML content"""
#     section = models.ForeignKey(Section, related_name='materials', on_delete=models.CASCADE)
#     title = models.CharField(max_length=255)
#     content_html = models.TextField(blank=True, default='')  # Добавляем default
#     original_file = models.FileField(upload_to='materials/', null=True, blank=True)
    
#     # Метаданные
#     has_images = models.BooleanField(default=False)
#     has_tables = models.BooleanField(default=False)
#     has_formulas = models.BooleanField(default=False)
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.title

# class MaterialImage(models.Model):
#     """Images extracted from materials"""
#     material = models.ForeignKey(Material, related_name='images', on_delete=models.CASCADE)
#     image = models.ImageField(upload_to='material_images/')
#     caption = models.CharField(max_length=255, blank=True, default='')
#     order = models.IntegerField(default=0)

#     class Meta:
#         ordering = ['order']

# learning_materials/models.py
from django.db import models

class Section(models.Model):
    """Main section of learning materials"""
    number = models.IntegerField()
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"{self.number}. {self.title}"

class Material(models.Model):
    """Learning material with HTML content"""
    section = models.ForeignKey(Section, related_name='materials', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content_html = models.TextField(default='', blank=True)  # HTML контент
    original_file = models.FileField(upload_to='materials/', null=True, blank=True)  # Оригинальный DOCX
    
    # Метаданные
    has_images = models.BooleanField(default=False)
    has_tables = models.BooleanField(default=False)
    has_formulas = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Проверьте в learning_materials/models.py, что поле image выглядит так:

class MaterialImage(models.Model):
    """Images extracted from materials"""
    material = models.ForeignKey(Material, related_name='images', on_delete=models.CASCADE)
    
    # Если поле image это ImageField, то нужно изменить на URLField или CharField
    # Старое (если так):
    # image = models.ImageField(upload_to='material_images/')
    
    # Новое (должно быть так для S3 URL):
    image = models.URLField(max_length=500)  # или CharField(max_length=500)
    
    caption = models.CharField(max_length=255, blank=True, default='')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']