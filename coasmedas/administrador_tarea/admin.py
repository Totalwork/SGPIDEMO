from django.contrib import admin
from .models import AEquipo,Colaborador,DTarea,DTareaAsignacion,SoporteAsignacionTarea

# Register your models here.
class AdminEquipo(admin.ModelAdmin):
	list_display=('nombre','descripcion','usuario_responsable','usuario_administrador',)
	search_fields=('nombre','descripcion',)
	list_filter=('nombre','descripcion',)		

admin.site.register(AEquipo,AdminEquipo)

class AdminColaborador(admin.ModelAdmin):
	list_display=('equipo','usuario',)
	search_fields=('equipo','usuario',)
	list_filter=('equipo','usuario',)		

admin.site.register(Colaborador,AdminColaborador)

class AdminTarea(admin.ModelAdmin):
	list_display=('asunto','descripcion','fecha_fin','colaborador_actual','numero','tipo_tarea','usuario_responsable',)
	search_fields=('colaborador_actual','usuario_responsable',)
	list_filter=('colaborador_actual','usuario_responsable',)		

admin.site.register(DTarea,AdminTarea)


class AdminAsignacionTarea(admin.ModelAdmin):
	list_display=('tarea','fecha','estado','comentario','solicitante',)
	search_fields=('tarea','estado','solicitante',)
	list_filter=('tarea','estado','solicitante',)		

admin.site.register(DTareaAsignacion,AdminAsignacionTarea)

class AdminSoporteAsignacionTarea(admin.ModelAdmin):
	list_display=('asignacion_tarea','nombre','ruta',)
	search_fields=('asignacion_tarea',)
	list_filter=('asignacion_tarea',)		

admin.site.register(SoporteAsignacionTarea,AdminSoporteAsignacionTarea)
