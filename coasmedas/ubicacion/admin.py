from django.contrib import admin
from .models import Ubicacion
# Register your models here.
class AdminUbicacion(admin.ModelAdmin):
	list_display=('nombre','latitud','longitud',)
	search_fields=('nombre','latitud','longitud',)

admin.site.register(Ubicacion,AdminUbicacion)