
from django.contrib import admin
from django.urls import path
from .views import listar_ordenes, eliminar_orden

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', listar_ordenes, name='listar_ordenes'),
    path('eliminar/<int:order_id>/', eliminar_orden, name='eliminar_orden'),
]

