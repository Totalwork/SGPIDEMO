from django.contrib import admin
from .models import SistemaVersion, ZInformacionArchivos, NombreArchivo
# Register your models here.

class AdminNombreArchivo(admin.ModelAdmin):
	"""docstring for AdminSistemaVersion"""
	list_display=('id', 'nombre',)
	list_filter=('nombre',)
	search_fields=('nombre',)	

class AdminSistemaVersion(admin.ModelAdmin):
	"""docstring for AdminSistemaVersion"""
	list_display=('version', 'fecha', 'activo',)
	list_filter=('version',)
	search_fields=('version',)	

class AdminInformacionArchivos(admin.ModelAdmin):
	"""docstring for AdminSistemaVersion"""
	list_display=('nombre_archivo', 'descripcion', 'sistema_version', 'archivo',)
	list_filter=('nombre_archivo', 'descripcion', 'sistema_version',)
	search_fields=('nombre_archivo', 'descripcion', 'sistema_version',)		

admin.site.register(NombreArchivo, AdminNombreArchivo)
admin.site.register(SistemaVersion, AdminSistemaVersion)
admin.site.register(ZInformacionArchivos, AdminInformacionArchivos)