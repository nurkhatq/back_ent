
from django.contrib import admin
# ent_trainer/urls.py (add to existing urls.py)
from django.urls import path, include

from ent_trainer import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.urls')),
    path('api/learning-materials/', include('learning_materials.urls')),
    path('api/context-questions/', include('context_questions.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)