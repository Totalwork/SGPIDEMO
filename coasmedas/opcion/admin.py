from django.contrib import admin
from .models import Opcion, Opcion_Usuario
# Register your models here.
class AdminOpcion(admin.ModelAdmin):
	list_display=('texto','destino','icono','orden','padre','permiso','urlActiva')
	search_fields=('texto',)
	list_filter=('padre',)

admin.site.register(Opcion,AdminOpcion)

class AdminOpcion_Usuario(admin.ModelAdmin):
	list_display=('opcion','usuario',)
	search_fields=('usuario',)

admin.site.register(Opcion_Usuario,AdminOpcion_Usuario)