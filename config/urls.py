from django.contrib import admin
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    path('health/', core_views.health, name='health'),
    path('ready/', core_views.ready, name='ready'),
    path('api/infraestructura/', core_views.infrastructure_status, name='infrastructure-status'),
    path('admin/', admin.site.urls),
    path('cuentas/', include('cuentas.urls')),
    path('estudiante/', include('estudiantes.urls')),
    path('empresa/', include('empresas.urls')),
    path('vacantes/', include('vacantes.urls')),
    path('api/v1/', include('api.urls')),
    path('', include('core.urls')),
]
