from django.contrib import admin
from .models import Proyecto_Actividad_contrato
# Register your models here.


class AdminProyecto_Actividad(admin.ModelAdmin):
	list_display = ('id','proyecto','actividad','valor')
	list_filter = ('proyecto','actividad__nombre',)
	search_fields = ('proyecto__nombre','actividad__nombre')

admin.site.register(Proyecto_Actividad_contrato,AdminProyecto_Actividad)