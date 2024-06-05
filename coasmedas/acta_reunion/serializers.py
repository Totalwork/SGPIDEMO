# -*- coding: utf-8 -*-
from rest_framework import viewsets, serializers, response
from django.db.models import Q

from .models import Consecutivo,Acta,Tema,Acta_historial,Participante_externo, \
Participante_interno,Compromiso,Compromiso_historial

from empresa.models import Empresa
from empresa.views import EmpresaSerializer, EmpresaLiteSerializer

from usuario.models import Usuario, Persona
from usuario.views import UsuarioSerializer, UsuarioLiteSerializer, PersonaSerializer, PersonaLiteSerializer

from tipo.models import Tipo
from tipo.views import TipoSerializer, TipoLiteSerializer

from estado.models import Estado
from estado.views import EstadoSerializer, EstadoLiteSerializer

from rest_framework import viewsets, serializers, response
from rest_framework.pagination import PageNumberPagination


from logs.models import Logs, Acciones
from sinin4.functions import functions

from .enumeration import estadoA,tipoAH,estadoC,tipoCH

#Serializadores de consecutivos
class ConsecutivoSerializer(serializers.HyperlinkedModelSerializer):	
	empresa = EmpresaSerializer(read_only=True)
	empresa_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Empresa.objects.all())

	class Meta: 
			model = Consecutivo
			fields=( 'id','ano','empresa','empresa_id','consecutivo')
			validators=[
						serializers.UniqueTogetherValidator(
						queryset=model.objects.all(),
						fields=( "empresa_id", "ano" ),
						message=('El año del consecutivo  no se puede repetir (anualidad , empresa).')
						)
						]

class ConsecutivoLiteSerializer(serializers.HyperlinkedModelSerializer):
	empresa = EmpresaLiteSerializer(read_only=True)
	class Meta: 
			model = Consecutivo
			fields=( 'id','ano','empresa','consecutivo')

	
#Serizlizadores de actas
class ActaSerializer(serializers.HyperlinkedModelSerializer):	

	controlador_actual = UsuarioSerializer(read_only=True)
	controlador_actual_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Usuario.objects.all())

	usuario_organizador = UsuarioSerializer(read_only=True)
	usuario_organizador_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Usuario.objects.all())
	
	acta_previa = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Acta.objects.all(),allow_null = True)

	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.filter(app='acta_reunion'),default=155)	

	class Meta: 
			model = Acta
			fields=( 'id',
					 'consecutivo',
					 'tema_principal',
					 'controlador_actual','controlador_actual_id',
					 'usuario_organizador','usuario_organizador_id',
					 'soporte',
					 'acta_previa',
					 'conclusiones',
					 'estado','estado_id',
					 'fecha',
					 'tiene_contrato','tiene_proyecto','tiene_conclusiones','tiene_compromisos')

	def get_fields(self):
		fields = super(ActaSerializer, self).get_fields()
		fields['acta_previa'] = ActaSerializer(read_only=True)
		return fields
	
class ActaLiteSerializer(serializers.HyperlinkedModelSerializer):	
	controlador_actual = UsuarioLiteSerializer(read_only=True)
	usuario_organizador = UsuarioLiteSerializer(read_only=True)
	estado = EstadoSerializer(read_only=True)
	acta_previa = serializers.SerializerMethodField(read_only=True)
	soporte = serializers.SerializerMethodField(read_only=True)

	class Meta: 
			model = Acta
			fields=( 'id',
					 'consecutivo',
					 'tema_principal',
					 'controlador_actual',
					 'usuario_organizador',
					 'acta_previa',
					 'estado',
					 'soporte',
					 'fecha',
					 'conclusiones',
					 'tiene_contrato','tiene_proyecto','tiene_conclusiones','tiene_compromisos',)

	def get_acta_previa(self,obj):
		if obj.acta_previa:
			return obj.acta_previa.consecutivo
		else:
			return 'No aplica'

	def get_soporte(self,obj):
		if obj.soporte:
			return True
		else:
			return False

	
#Serizlizadores de temas
class TemaSerializer(serializers.HyperlinkedModelSerializer):
	acta = ActaSerializer(read_only=True)
	acta_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Acta.objects.all())

	class Meta: 
			model = Tema
			fields=( 'id','acta','acta_id','tema')

class TemaLiteSerializer(serializers.HyperlinkedModelSerializer):
	acta = serializers.SerializerMethodField(read_only=True)
	class Meta: 
			model = Tema
			fields=( 'id','acta','tema')

	def get_acta(self,obj):
		if obj.acta:
			return obj.acta.consecutivo
		else:
			return None


#Serializadores de historial de acta
class Acta_historialSerializer(serializers.HyperlinkedModelSerializer):
	acta = ActaSerializer(read_only=True)
	acta_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Acta.objects.all())

	tipo_operacion = TipoSerializer(read_only=True)
	tipo_operacion_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='acta_reunion_historial'))
	
	controlador = UsuarioSerializer(read_only=True)
	controlador_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Usuario.objects.all())

	class Meta: 
			model = Acta_historial
			fields=( 'id',
					 'acta','acta_id',
					 'fecha',
					 'tipo_operacion','tipo_operacion_id',
					 'motivo',
					 'controlador','controlador_id')

class Acta_historialLiteSerializer(serializers.HyperlinkedModelSerializer):
	acta = serializers.SerializerMethodField(read_only=True)
	tipo_operacion = TipoLiteSerializer(read_only=True)
	controlador = UsuarioLiteSerializer(read_only=True)

	class Meta: 
			model = Acta_historial
			fields=( 'id','acta','fecha','tipo_operacion','motivo','controlador')

	def get_acta(self,obj):
		if obj.acta:
			return obj.acta.consecutivo
		else:
			return None




#Serializadores de participantes externos
class Participante_externoSerializer(serializers.HyperlinkedModelSerializer):
	acta = ActaSerializer(read_only=True)
	acta_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Acta.objects.all())

	persona = PersonaSerializer(read_only=True)
	persona_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Persona.objects.all())

	class Meta: 
			model = Participante_externo
			fields=( 'id',
					 'acta','acta_id',
					 'persona','persona_id',
					 'asistio')

class Participante_externoLiteSerializer(serializers.HyperlinkedModelSerializer):
	acta = serializers.SerializerMethodField(read_only=True)
	persona = PersonaLiteSerializer(read_only=True)

	class Meta: 
			model = Participante_externo
			fields=( 'id','acta','persona','asistio')

	def get_acta(self,obj):
		if obj.acta:
			return obj.acta.consecutivo
		else:
			return None




#Serializadores de participantes internos
class Participante_internoSerializer(serializers.HyperlinkedModelSerializer):
	acta = ActaSerializer(read_only=True)
	acta_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Acta.objects.all())

	usuario = UsuarioSerializer(read_only=True)
	usuario_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Usuario.objects.all())

	class Meta: 
			model = Participante_interno
			fields=( 'id',
					 'acta','acta_id',
					 'usuario','usuario_id',
					 'asistio')

class Participante_internoLiteSerializer(serializers.HyperlinkedModelSerializer):
	acta = serializers.SerializerMethodField(read_only=True)
	usuario = UsuarioLiteSerializer(read_only=True)

	class Meta: 
			model = Participante_interno
			fields=( 'id','acta','usuario','asistio')

	def get_acta(self,obj):
		if obj.acta:
			return obj.acta.consecutivo
		else:
			return None





#Serializadores de compromisos
class CompromisoSerializer(serializers.HyperlinkedModelSerializer):
	acta = ActaSerializer(read_only=True)
	acta_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Acta.objects.all())

	supervisor = UsuarioSerializer(read_only=True)
	supervisor_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Usuario.objects.all())

	participante_responsable = Participante_externoSerializer(read_only=True)
	participante_responsable_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Participante_externo.objects.all(), allow_null=True)

	usuario_responsable = UsuarioSerializer(read_only=True)
	usuario_responsable_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Usuario.objects.all())

	estado = EstadoSerializer(read_only=True)
	estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.all(),default=estadoC.por_cumplir)

	class Meta: 
			model = Compromiso
			fields=( 'id',
					 'acta','acta_id',
					 'supervisor','supervisor_id',
					 'responsable_interno',
					 'participante_responsable','participante_responsable_id',
					 'usuario_responsable','usuario_responsable_id',
					 'fecha_compromiso',
					 'fecha_proximidad',
					 'descripcion',
					 'estado','estado_id',
					 'requiere_soporte',
					 'soporte',
					 'notificar_organizador',
					 'notificar_controlador',
					 )

class CompromisoLiteSerializer(serializers.HyperlinkedModelSerializer):
	acta = serializers.SerializerMethodField(read_only=True)	

	supervisor = UsuarioLiteSerializer(read_only=True)
	usuario_responsable =  UsuarioLiteSerializer(read_only=True)

	cumplimiento = serializers.SerializerMethodField(read_only=True)
	cant_prorrogas = serializers.SerializerMethodField(read_only=True)

	participante_responsable = Participante_externoLiteSerializer(read_only=True)
	estado = EstadoSerializer(read_only=True)


	class Meta: 
			model = Compromiso
			fields=( 'id',
					 'descripcion',
					 'acta',
					 'supervisor',
					 'usuario_responsable',
					 'fecha_compromiso',
					 'fecha_proximidad',
					 'cumplimiento',
					 'cant_prorrogas',
					 'responsable_interno',
					 'requiere_soporte',
					 'estado',
					 'soporte',
					 'participante_responsable',
					 'notificar_organizador',
					 'notificar_controlador',
					 ) 

	def get_acta(self,obj):
		if obj.acta:
			return {'id':obj.acta.id,'consecutivo':obj.acta.consecutivo}
		else:
			return None


	def get_cumplimiento(self,obj):
		if Compromiso_historial.objects.filter(compromiso__id=obj.id,tipo_operacion__id=tipoCH.cumplimiento).exists():
			historial = Compromiso_historial.objects.filter(compromiso__id=obj.id,tipo_operacion__id=tipoCH.cumplimiento).order_by('fecha')
			fecha_cumplimiento = historial.last().fecha
			motivo = historial.last().motivo
			return {'fecha_cumplimiento':fecha_cumplimiento,'motivo':motivo}
		else:
			return None

	def get_cant_prorrogas(self,obj):
		cant = 0
		if Compromiso_historial.objects.filter(compromiso__id=obj.id,tipo_operacion__id=tipoCH.proroga).exists():
			cant = Compromiso_historial.objects.filter(compromiso__id=obj.id,tipo_operacion__id=tipoCH.proroga).count()			
		return cant



#Serializadores de historial de compromisos
class Compromiso_historialSerializer(serializers.HyperlinkedModelSerializer):
	compromiso = CompromisoSerializer(read_only=True)
	compromiso_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Compromiso.objects.all())

	tipo_operacion = TipoSerializer(read_only=True)
	tipo_operacion_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.all())

	participante_externo = Participante_externoSerializer(read_only=True)
	participante_externo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Participante_externo.objects.all())

	participante_interno = Participante_internoSerializer(read_only=True)
	participante_interno_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Participante_interno.objects.all())

	class Meta: 
			model = Compromiso_historial
			fields=( 'id',
					 'compromiso','compromiso_id',
					 'fecha',
					 'tipo_operacion','tipo_operacion_id',
					 'motivo',
					 'participante_externo','participante_externo_id',
					 'participante_interno','participante_interno_id')

class Compromiso_historialLiteSerializer(serializers.HyperlinkedModelSerializer):
	compromiso = CompromisoLiteSerializer(read_only=True)
	tipo_operacion = TipoLiteSerializer(read_only=True)
	participante = serializers.SerializerMethodField(read_only=True)

	class Meta: 
			model = Compromiso_historial
			fields=( 'id','fecha','compromiso','tipo_operacion','motivo','participante')

	def get_participante(self,obj):
		
		if obj.participante_externo:
			return {
				'id':obj.participante_externo.id,
				'nombre_completo':obj.participante_externo.persona.nombres+' '+obj.participante_externo.persona.apellidos,
				'tipo_participante':'Externo'}

		elif obj.participante_interno:
			return {
				'id':obj.participante_interno.id,
				'nombre_completo':obj.participante_interno.usuario.persona.nombres+' '+obj.participante_interno.usuario.persona.apellidos,
				'tipo_participante':'Interno'}
	

class NoParticipantesSerializer(serializers.HyperlinkedModelSerializer):	
	nombre_completo = serializers.SerializerMethodField(read_only=True)
	usuario = serializers.SerializerMethodField(read_only=True)
	empresa = serializers.SerializerMethodField(read_only=True)

	class Meta: 
			model = Persona
			fields=( 'id',
					 'nombre_completo',
					 'usuario',
					 'empresa',
					 )	

	def get_nombre_completo(self,obj):		
		return obj.nombres+' '+obj.apellidos

	def get_usuario(self,obj):
		validator = Usuario.objects.filter(persona_id=obj.id,user__is_active=True)
		if validator:			
			model_usuario = validator
			return model_usuario[0].id
		else:
			return None

	def get_empresa(self,obj):
		#print(obj.id)
		if Usuario.objects.filter(persona__id=obj.id).exists():
			empresa=Usuario.objects.filter(persona__id=obj.id).values('empresa__nombre')			
			return empresa[0]['empresa__nombre']
		else:
			return None
