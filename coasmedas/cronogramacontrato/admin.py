from django.contrib import admin
from cronogramacontrato.models import CcCronograma, CcCapitulo, CcActividad, CcActividadContrato, CcActividadContratoSoporte, CcActividadContratoResponsable
from estado.models import Estado
from contrato.models import Contrato


class AdminCronograma(admin.ModelAdmin):
    list_display=('nombre','activo')
    list_filter=('nombre','activo')
    search_fields=('nombre',)


class AdminCapitulo(admin.ModelAdmin):
    list_display=('nombre','cronograma','orden',)
    list_filter=('nombre','cronograma','orden',)
    search_fields=('nombre','cronograma', 'orden')


class AdminActividad(admin.ModelAdmin):
    list_display=('capitulo','orden','descripcion','inicioprogramado','finprogramado',
    'requiereSoporte','soporteObservaciones',)
    list_filter=('capitulo','orden','descripcion','inicioprogramado','finprogramado','requiereSoporte',)
    search_fields=('capitulo','orden',)


class AdminActividadContrato(admin.ModelAdmin):
    list_display=('actividad','contrato','inicioprogramado','finprogramado','inicioejecutado',
    'finejecutado','estadoinicio','estadofin','observaciones',)
    list_filter=('actividad','contrato','inicioprogramado','finprogramado','inicioejecutado',
    'finejecutado','estadoinicio','estadofin','observaciones',)
    search_fields=('actividad','contrato','observaciones',)

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['contrato'].queryset = Contrato.objects.filter(tipo_contrato__id=12)
        context['adminform'].form.fields['estadoinicio'].queryset = Estado.objects.filter(
            app='cronogramacontrato_estadoinicio')
        context['adminform'].form.fields['estadofin'].queryset = Estado.objects.filter(
            app='cronogramacontrato_estadofin')
        return super(AdminActividadContrato, self).render_change_form(request, context, *args, **kwargs)


class AdminActividadContratoSoporte(admin.ModelAdmin):
    list_display=('actividadcontrato','nombre','archivo',)
    list_filter=('actividadcontrato','nombre','archivo',)
    search_fields=('nombre',)


class AdminActividadContratoResponsable(admin.ModelAdmin):
    list_display=('actividadcontrato','usuario',)
    list_filter=('actividadcontrato','usuario',)
    search_fields=('actividadcontrato','usuario',)


admin.site.register(CcCronograma,AdminCronograma)
admin.site.register(CcCapitulo,AdminCapitulo)
admin.site.register(CcActividad,AdminActividad)
admin.site.register(CcActividadContrato,AdminActividadContrato)
admin.site.register(CcActividadContratoSoporte,AdminActividadContratoSoporte)
admin.site.register(CcActividadContratoResponsable,AdminActividadContratoResponsable)