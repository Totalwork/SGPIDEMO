from django.contrib import admin
from .models import Servidumbre_documento, Servidumbre_expediente, Servidumbre_grupo_documento, Servidumbre_persona, Servidumbre_predio, Servidumbre_predio_documento
from proyecto.models import Proyecto
from usuario.models import Usuario
from estado.models import Estado
from tipo.models import Tipo

class AdminServidumbreDocumento(admin.ModelAdmin):
	list_display=('grupo_documento', 'nombre',)
	list_filter=('grupo_documento',)
	search_fields=('nombre',)

class AdminServidumbreExpediente(admin.ModelAdmin):
	list_display=('id','proyecto', 'fecha_creacion','usuario_creador','estado',)
	list_filter=('estado',)
	search_fields=('proyecto__nombre','estado__nombre')

class AdminServidumbreGrupoDocumento(admin.ModelAdmin):
	list_display=('nombre',)
	search_fields=('nombre',)

class AdminServidumbrePersona(admin.ModelAdmin):	
	list_display=('cedula','nombres','apellidos','celular','telefono',)
	search_fields=('nombres', 'apellidos', 'cedula',)

class AdminServidumbrePredio(admin.ModelAdmin):
	list_display=('id','expediente','persona','nombre_direccion','tipo','grupo_documento',)
	list_filter=('persona', 'tipo',)
	search_fields=('persona__nombres', 'expediente__proyecto__nombre','expediente__usuario_creador__user__username')

class AdminServidumbrePredioDocumento(admin.ModelAdmin):
	list_display=('predio','documento','archivo','nombre')
	list_filter=('predio',)
	search_fields=('predio__nombre_direccion' ,'documento__nombre',)	


admin.site.register(Servidumbre_documento, AdminServidumbreDocumento)
admin.site.register(Servidumbre_expediente, AdminServidumbreExpediente)
admin.site.register(Servidumbre_grupo_documento, AdminServidumbreGrupoDocumento)
admin.site.register(Servidumbre_persona, AdminServidumbrePersona)
admin.site.register(Servidumbre_predio, AdminServidumbrePredio)
admin.site.register(Servidumbre_predio_documento, AdminServidumbrePredioDocumento)

# Register your models here.
