from django.contrib import admin
from .models import Departamento, Municipio, Banco, Cargo, \
Funcionario, Notificacion, VideosTutoriales, GrupoVideosTutoriales
from empresa.models import Empresa
from usuario.models import Persona
# Register your models here.
class AdminDepartamento(admin.ModelAdmin):
	list_display=('nombre','iniciales')
	search_fields=('nombre','iniciales',)

class AdminMunicipio(admin.ModelAdmin):
	list_display=('nombre','departamento')
	#list_filter=('departamento',)
	search_fields=('nombre',)

class AdminBanco(admin.ModelAdmin):
	list_display=('nombre','codigo_bancario')
	#list_filter=('departamento',)
	search_fields=('nombre',)

class AdminCargo(admin.ModelAdmin):
	list_display=('nombre','empresa','firma_cartas')
	list_filter=('empresa',)
	search_fields=('nombre',)

class AdminFuncionario(admin.ModelAdmin):
	list_display=('empresa','persona','cargo','iniciales','activo')
	list_filter=('empresa','persona','notificaciones')
	search_fields=('empresa__nombre','persona__cedula', 'persona__nombres', 'persona__apellidos', 'iniciales',)

class AdminNotificacion(admin.ModelAdmin):
	list_display=('nombre','tabla_referencia')
	search_fields=('nombre','tabla_referencia',)
	list_filter=('tabla_referencia',)		

class AdminGrupoVideosTutoriales(admin.ModelAdmin):
	list_display=('nombre',)
	search_fields=('nombre',)
	list_filter=('nombre',)	

class AdminVideosTutoriales(admin.ModelAdmin):
	list_display=('titulo', 'grupo',)
	search_fields=('titulo', 'grupo',)
	list_filter=('titulo', 'grupo',)			

admin.site.register(Departamento,AdminDepartamento)
admin.site.register(Municipio,AdminMunicipio)
admin.site.register(Banco,AdminBanco)
admin.site.register(Cargo,AdminCargo)
admin.site.register(Funcionario,AdminFuncionario)
admin.site.register(Notificacion,AdminNotificacion)
admin.site.register(GrupoVideosTutoriales,AdminGrupoVideosTutoriales)
admin.site.register(VideosTutoriales,AdminVideosTutoriales)