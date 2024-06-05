from django.contrib import admin
from estado.models import Estado, Estados_posibles
# Register your models here.
class AdminEstado(admin.ModelAdmin):
	list_display=('id','app','nombre','color','icono','codigo',)
	list_filter = ('app','nombre',)
	search_fields= ('app','nombre',)

class AdminEstados_posibles(admin.ModelAdmin):
	list_display=('actual','siguiente',)

admin.site.register(Estado,AdminEstado)
admin.site.register(Estados_posibles,AdminEstados_posibles)