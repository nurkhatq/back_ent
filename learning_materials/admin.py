from django.contrib import admin

# Register your models here.
from .models import Section, Material, MaterialImage
admin.site.register(Section)
admin.site.register(Material)
admin.site.register(MaterialImage)