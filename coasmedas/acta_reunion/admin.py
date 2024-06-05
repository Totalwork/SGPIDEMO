from django.contrib import admin
from .models import Consecutivo,Acta,Tema,Acta_historial,Participante_externo,Participante_interno,Compromiso,Compromiso_historial
from proyecto.models import Proyecto
from proyecto.models import Contrato
from usuario.models import Usuario
from estado.models import Estado
from tipo.models import Tipo

class AdminConsecutivo(admin.ModelAdmin):
	list_display=('ano', 'empresa','consecutivo',)
	list_filter=('ano','empresa',)
	search_fields=('ano','consecutivo','empresa__nombre')

class AdminActa(admin.ModelAdmin):
	list_display=('consecutivo', 'acta_previa','fecha','controlador_actual','usuario_organizador','tema_principal','estado')
	list_filter=('estado','controlador_actual','usuario_organizador')
	search_fields=('consecutivo','tema_principal','controlador_actual__persona__nombres','controlador_actual__persona__apellidos','usuario_organizador__persona__nombres','usuario_organizador__persona__apellidos')

class AdminTema(admin.ModelAdmin):
	list_display=('acta', 'tema',)
	list_filter=('acta',)
	search_fields=('tema','acta__consecutivo')

class AdminActa_historial(admin.ModelAdmin):
	list_display=('acta', 'fecha','tipo_operacion','controlador','fecha')
	list_filter=('acta','tipo_operacion',)
	search_fields=('acta__consecutivo','tipo_operacion','fecha')

class AdminParticipante_interno(admin.ModelAdmin):
	list_display=('acta', 'usuario','asistio')
	list_filter=('acta','asistio')
	search_fields=('acta__consecutivo','usuario__persona__nombres','usuario__persona__apellidos')

class AdminParticipante_externo(admin.ModelAdmin):
	list_display=('acta', 'persona','asistio')
	list_filter=('acta','asistio')
	search_fields=('acta__consecutivo','persona__nombres','persona__apellidos')


class AdminCompromiso(admin.ModelAdmin):
	list_display=('acta', 'fecha_compromiso','estado','supervisor','responsable_interno','participante_responsable','usuario_responsable')
	list_filter=('acta','responsable_interno','estado',)
	search_fields=('acta__consecutivo','fecha_compromiso')

class AdminCompromiso_historial(admin.ModelAdmin):
	list_display=('compromiso', 'fecha','tipo_operacion',)
	list_filter=('compromiso','tipo_operacion')
	search_fields=('compromiso__descripcion','fecha','tipo_operacion')



admin.site.register(Consecutivo, AdminConsecutivo)
admin.site.register(Acta, AdminActa)
admin.site.register(Tema, AdminTema)
admin.site.register(Acta_historial, AdminActa_historial)
admin.site.register(Participante_externo, AdminParticipante_externo)
admin.site.register(Participante_interno, AdminParticipante_interno)
admin.site.register(Compromiso, AdminCompromiso)
admin.site.register(Compromiso_historial, AdminCompromiso_historial)
# Register your models here.
