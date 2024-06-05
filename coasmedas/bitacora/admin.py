from django.contrib import admin
from .models import Bitacora
# Register your models here.

class AdminBitacora(admin.ModelAdmin):
	"""docstring for AdminSistemaVersion"""
	list_display=('id', 'usuario','proyecto', 'fecha', 'comentario')
	list_filter=('usuario__persona__nombres', 'usuario__persona__apellidos', 'proyecto__nombre')
	search_fields=('usuario__persona__nombres', 'usuario__persona__apellidos', 'proyecto__nombre')

admin.site.register(Bitacora, AdminBitacora)