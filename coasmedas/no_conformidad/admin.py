from django.contrib import admin
from .models import NoConformidad

# Register your models here.
class AdminNoConformidad(admin.ModelAdmin):   
	list_display=('proyecto','usuario','estado','detectada','descripcion_no_corregida','descripcion_corregida','fecha_no_corregida','fecha_corregida','terminada',
					'estructura','primer_correo','segundo_correo','tercer_correo', 'tipo', 'valoracion')
	list_filter=('estado', 'proyecto', 'tipo', 'valoracion')
	search_fields=('proyecto',)

admin.site.register(NoConformidad, AdminNoConformidad)