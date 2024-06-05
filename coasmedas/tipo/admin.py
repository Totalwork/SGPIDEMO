from django.contrib import admin
from tipo.models import Tipo, Tipos_posibles
# Register your models here.
class AdminTipo(admin.ModelAdmin):
	list_display=('app','nombre','color','icono','codigo',)
	list_filter = ('app','nombre', )
	search_fields= ('app','nombre',)

class AdminTipos_posibles(admin.ModelAdmin):
	list_display=('actual','siguiente',)

admin.site.register(Tipo,AdminTipo)
admin.site.register(Tipos_posibles,AdminTipos_posibles)

