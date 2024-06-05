from django.contrib import admin
from logs.models import Logs
# Register your models here.
class AdminLogs(admin.ModelAdmin):
	list_display=('fecha_hora','usuario','accion','nombre_modelo','id_manipulado')
	search_fields=('usuario','accion','nombre_modelo','id_manipulado')
	list_filter=('usuario','accion','nombre_modelo','id_manipulado')

admin.site.register(Logs,AdminLogs)	
