from django.contrib import admin
from contrato.models import Contrato, VigenciaContrato, EmpresaContrato, Rubro, Sub_contratista, Contrato_cesion, Cesion_economica
from contrato.models import ActaAsignacionRecursos, ActaAsignacionRecursosContrato, Contrato_supervisor
# Register your models here.
class AdminContrato(admin.ModelAdmin):
	list_display=('id','nombre','numero','tipo_contrato','descripcion','estado','contratista','contratante','mcontrato','activo')
	list_filter=('tipo_contrato','estado','contratista','contratante',)
	search_fields=('nombre','numero',)

class AdminVigenciaContrato(admin.ModelAdmin):
	list_display=('nombre','contrato','tipo','fecha_inicio','fecha_fin','valor','soporte')
	list_filter=('contrato','tipo',)
	search_fields=('nombre','contrato__nombre','tipo__nombre',)

class AdminEmpresaContrato(admin.ModelAdmin):
	list_display=('contrato','empresa','participa','edita')
	list_filter=('contrato','empresa',)
	search_fields=('contrato__nombre','empresa__nombre',)

class AdminRubro(admin.ModelAdmin):
	list_display=('nombre',)
	list_filter=('nombre',)
	search_fields=('nombre',)

class AdminSubContratista(admin.ModelAdmin):
	list_display=('contrato','empresa','soporte')
	list_filter=('contrato','empresa',)
	search_fields=('contrato__nombre','empresa__nombre',)

class AdminContratoCesion(admin.ModelAdmin):
	list_display=('contrato','contratista_nuevo','contratista_antiguo','fecha','soporte')
	list_filter=('contrato','contratista_nuevo','contratista_antiguo',)
	search_fields=('contrato__nombre','contratista_nuevo','contratista_antiguo__nombre',)

class AdminCesionEconomica(admin.ModelAdmin):
	list_display=('contrato','empresa','fecha','soporte')
	list_filter=('contrato','empresa',)
	search_fields=('contrato__nombre','empresa__nombre',)

class AdminActaAsignacionRecursos(admin.ModelAdmin):
	list_display = ('id','nombre','fechafirma','archivo')
	list_filter = ('fechafirma',)
	search_fields = ('nombre',)

class AdminActaAsignacionRecursosContrato(admin.ModelAdmin):
	list_display = ('id','actaAsignacion','contrato')
	list_filter = ('actaAsignacion',)
	search_fields = ('contrato','actaAsignacion',)

	def render_change_form(self, request, context, *args, **kwargs):
		context['adminform'].form.fields['contrato'].queryset = Contrato.objects.filter(tipo_contrato__id=12)
		return super(AdminActaAsignacionRecursosContrato, self).render_change_form(request, context, *args, **kwargs)

class AdminContratoSupervisor(admin.ModelAdmin):
	list_display = ('id','contrato','funcionario','empresa','cargo')
	list_filter = ('empresa',)
	search_fields = ('contrato__nombre','empresa__nombre')

admin.site.register(Contrato,AdminContrato)
admin.site.register(VigenciaContrato,AdminVigenciaContrato)
admin.site.register(EmpresaContrato,AdminEmpresaContrato)
admin.site.register(Rubro,AdminRubro)
admin.site.register(Sub_contratista,AdminSubContratista)
admin.site.register(Contrato_cesion,AdminContratoCesion)
admin.site.register(Cesion_economica,AdminCesionEconomica)
admin.site.register(ActaAsignacionRecursos,AdminActaAsignacionRecursos)
admin.site.register(ActaAsignacionRecursosContrato,AdminActaAsignacionRecursosContrato)
admin.site.register(Contrato_supervisor,AdminContratoSupervisor)
