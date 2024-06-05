from django.contrib import admin
from .models import AEscolaridad, AMatricula, Requerimientos, \
RequerimientosValor, Empleado, Novedad, Planilla, EmpresaPermiso, Cargo, CorreoContratista, ZRequerimientosEmpleados

class AdminEmpleado(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('cedula','persona','nombre_contratista', 'empresa')
	search_fields=('persona__nombres','persona__apellidos','persona__cedula','contratista__nombre',)

	def cedula(self, obj):
		return obj.persona.cedula	

	def nombre_contratista(self, obj):
		return obj.contratista.nombre if obj.contratista is not None else 'En estudio'

class AdminNovedad(admin.ModelAdmin):
	"""docstring for AdminNovedad"""
	list_display=('cedula','persona','estado',)
	search_fields=('empleado__persona__nombres','empleado__persona__apellidos','empleado__persona__cedula',)	
	
	def cedula(self, obj):
		return obj.empleado.persona.cedula	

	def persona(self, obj):
		return obj.empleado.persona

class AdminPlanilla(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('nombre_contratista','nombre_mes', 'fecha_limite','fecha_pago','estado')
	search_fields=('contratista__nombre','mes','fecha_limite')

	def nombre_contratista(self, obj):
		return obj.contratista.nombre

	def nombre_mes(self, obj):
		meses=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
		return meses[obj.mes - 1]

class AdminEmpresaPermiso(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('nombre_empresa','nombre_empresa_acceso',)
	search_fields=('empresa_acceso__nombre','empresa__nombre')

	def nombre_empresa_acceso(self, obj):
		return obj.empresa_acceso.nombre

	def nombre_empresa(self, obj):
		return obj.empresa.nombre	

class AdminEscolaridad(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('nombre',)
	search_fields=('nombre',)	
		

class AdminMatricula(admin.ModelAdmin):
	list_display=('nombre',)
	search_fields=('nombre',)	


class AdminRequerimientos(admin.ModelAdmin):
	list_display=('nombre',)
	search_fields=('nombre',)


class AdminRequerimientosValor(admin.ModelAdmin):
	list_display=('nombre',)
	search_fields=('nombre',)

class AdminCargo(admin.ModelAdmin):
	list_display=('id', 'nombre', 'soporte_tsa', 'soporte_matricula', 'hoja_de_vida',)
	search_fields=('nombre',)	

class AdminCorreoContratista(admin.ModelAdmin):
	list_display=('nombre_contratista','correo',)
	search_fields=('contratista__nombre','correo',)

	def nombre_contratista(self, obj):
		return obj.contratista.nombre

class AdminRequerimientosEmpleados(admin.ModelAdmin):
	list_display=('empleado', 'requerimiento','requerimiento_valor',)
	search_fields=('empleado__persona__cedula', 'empleado__persona__nombres', 'empleado__persona__apellidos', 'requerimiento__nombre','requerimiento_valor__nombre',)

# Register your models here.

admin.site.register(AEscolaridad, AdminEscolaridad)
admin.site.register(AMatricula, AdminMatricula)
admin.site.register(Requerimientos, AdminRequerimientos)
admin.site.register(RequerimientosValor, AdminRequerimientosValor)
admin.site.register(Empleado, AdminEmpleado)
admin.site.register(Novedad, AdminNovedad)
admin.site.register(Planilla, AdminPlanilla)
admin.site.register(EmpresaPermiso, AdminEmpresaPermiso)
admin.site.register(Cargo, AdminCargo)
admin.site.register(CorreoContratista, AdminCorreoContratista)
admin.site.register(ZRequerimientosEmpleados, AdminRequerimientosEmpleados)