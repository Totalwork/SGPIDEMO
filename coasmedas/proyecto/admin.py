from django.contrib import admin
from .models import P_fondo, P_tipo, Proyecto, Proyecto_historial_estado, Proyecto_empresas , Proyecto_campo_info_tecnica , Proyecto_info_tecnica, Contrato_fondo
from empresa.models import Empresa
from usuario.models import Persona
from parametrizacion.models import Departamento

# Register your models here.
class AdminProyectoFondo(admin.ModelAdmin):
	list_display=('nombre' , 'descripcion')
	list_filter=('nombre', )
	search_fields=('nombre',)

class AdminProyectoTipo(admin.ModelAdmin):
	list_display=('nombre' , 'fondo_proyecto')
	list_filter=('nombre', 'fondo_proyecto',)
	search_fields=('nombre',)	

class AdminProyecto(admin.ModelAdmin):
	list_display=('mcontrato' , 'municipio' , 'nombre' , 'entidad_bancaria' , 'tipo_cuenta' ,'No_cuenta' , 'estado_proyecto' )
	list_filter=('mcontrato', 'municipio','nombre',)
	search_fields=('nombre',)	

class AdminProyectoHistorialEstado(admin.ModelAdmin):
	list_display=('proyecto' , 'estado_proyecto' )
	list_filter=('proyecto', 'estado_proyecto',)
	search_fields=('proyecto',)	

class AdminProyectoEmpresas(admin.ModelAdmin):
	list_display=( 'proyecto' , 'empresa')
	list_filter=('proyecto', 'empresa',)
	search_fields=('proyecto',)	

class AdminProyectoCampoInfoTecnica(admin.ModelAdmin):
	list_display=('nombre' , 'tipo_proyecto')
	list_filter=('nombre', 'tipo_proyecto',)
	search_fields=('tipo_proyecto',)

class AdminProyectoInfoTecnica(admin.ModelAdmin):
	list_display=('proyecto' , 'campo')
	list_filter=('proyecto', 'campo',)
	search_fields=('proyecto',)

class AdminContratoFondo(admin.ModelAdmin):
	list_display=('fondo', 'contrato')
	list_filter=('fondo', 'contrato',)
	search_fields=('contrato',)

admin.site.register(P_fondo, AdminProyectoFondo)
admin.site.register(P_tipo, AdminProyectoTipo)
admin.site.register(Proyecto, AdminProyecto)
admin.site.register(Proyecto_historial_estado, AdminProyectoHistorialEstado)
admin.site.register(Proyecto_empresas, AdminProyectoEmpresas)	
admin.site.register(Proyecto_campo_info_tecnica, AdminProyectoCampoInfoTecnica)
admin.site.register(Proyecto_info_tecnica, AdminProyectoInfoTecnica)
admin.site.register(Contrato_fondo, AdminContratoFondo)