from django.shortcuts import render, render_to_response
from django.urls import reverse

from rest_framework import viewsets, serializers, response
from django.db.models import Q

from .models import Servidumbre_expediente, Servidumbre_grupo_documento
from .models import Servidumbre_documento, Servidumbre_persona, Servidumbre_predio, Servidumbre_predio_documento, Servidumbre_predio_georeferencia


from proyecto.models import Proyecto 
from contrato.models import Contrato
from usuario.models import Usuario
from usuario.views import *

from tipo.models import Tipo
from tipo.views import *

from estado.models import Estado
from estado.views import EstadoSerializer


from rest_framework import status
from rest_framework.pagination import PageNumberPagination


from logs.models import Logs, Acciones
from coasmedas.functions import functions



# Serializer de proyecto
class ProyectoLiteSerializer(serializers.HyperlinkedModelSerializer):
	departamento = serializers.SerializerMethodField(read_only=True)
	municipio = serializers.SerializerMethodField(read_only=True)
	nombremcontrato = serializers.SerializerMethodField(read_only=True)

	class Meta: 
		model = Proyecto
		fields=( 'id','nombre','municipio','departamento','nombremcontrato')

	def get_departamento(self,obj):
		return Proyecto.objects.get(pk=obj.id).municipio.departamento.nombre

	def get_municipio(self,obj):
		return Proyecto.objects.get(pk=obj.id).municipio.nombre

	def get_nombremcontrato(self,obj):
		return Contrato.objects.get(
			pk=Proyecto.objects.get(
				pk=obj.id
				).mcontrato.id
			).nombre

# Serializer de	usuario
class UsuarioLiteSerializer(serializers.HyperlinkedModelSerializer):    

    persona = PersonaLiteSerializer(read_only=True)

    class Meta:
        model = Usuario
        fields=('id','persona') 


class ExpedienteLiteEditarSerializer(serializers.HyperlinkedModelSerializer):
	proyecto = ProyectoLiteSerializer(read_only=True)
	
	class Meta:
		model = Servidumbre_expediente
		fields = fields=('id', 'proyecto', )


##LiteSerializer
class Servidumbre_expedienteLiteSerializer(serializers.HyperlinkedModelSerializer):
	proyecto = ProyectoLiteSerializer(read_only=True)
	usuario_creador = UsuarioLiteSerializer(read_only=True)
	estado = EstadoSerializer(read_only=True)

	class Meta:
		model = Servidumbre_expediente
		fields = fields=('id', 'proyecto', 'fecha_creacion', 'usuario_creador', 'estado')

	
##Serializer
class Servidumbre_expedienteSerializer(serializers.HyperlinkedModelSerializer):
	proyecto = ProyectoLiteSerializer(read_only=True)
	proyecto_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Proyecto.objects.all())

	#usuario_creador = UsuarioLiteSerializer(read_only=True)
	usuario_creador_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Usuario.objects.all())

	estado = EstadoSerializer(read_only=True)
	#estado_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Estado.objects.all())

	nopredios = serializers.SerializerMethodField(read_only=True)
	class Meta:
		model = Servidumbre_expediente
		fields=('id', 'proyecto','proyecto_id', 'fecha_creacion',
			'usuario_creador_id', 'estado','nopredios',)

		validators=[
				serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=( 'proyecto_id',),
				message=('El proyecto no puede  estar repetido en diferentes expediente.')
				)
				]

	def get_nopredios(self,obj):
		return Servidumbre_predio.objects.filter(expediente_id=obj.id).count()




##LiteSerializer
class Servidumbre_grupo_documentoLiteSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Servidumbre_grupo_documento
		fields = ('id', 'nombre')
##Serializer
class Servidumbre_grupo_documentoSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Servidumbre_grupo_documento
		fields=('id', 'nombre')







##LiteSerializer
class Servidumbre_documentoLiteSerializer(serializers.HyperlinkedModelSerializer):
	grupo_documento = Servidumbre_grupo_documentoLiteSerializer(read_only=True)

	class Meta:
		model = Servidumbre_documento
		fields = ('id', 'grupo_documento', 'nombre')
##Serializer
class Servidumbre_documentoSerializer(serializers.HyperlinkedModelSerializer):

	grupo_documento = Servidumbre_grupo_documentoLiteSerializer(read_only=True)
	grupo_documento_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Servidumbre_grupo_documento.objects.all())

	class Meta:
		model = Servidumbre_documento
		fields=('id', 'grupo_documento','grupo_documento_id', 'nombre')
		validators=[
				serializers.UniqueTogetherValidator(
				queryset=model.objects.all(),
				fields=( 'grupo_documento_id', 'nombre'),
				message=('El documento no puede  estar repetido en la mismo grupo.')
				)
				]






##LiteSerializer
class Servidumbre_personaLiteSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Servidumbre_persona
		fields = ('id', 'nombres','apellidos')
##Serializer
class Servidumbre_personaSerializer(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model = Servidumbre_persona
		fields=('id', 'cedula', 'nombres', 'apellidos', 'celular', 'telefono')






##LiteSerializer
class Servidumbre_predioLiteSerializer(serializers.HyperlinkedModelSerializer):
	expediente = Servidumbre_expedienteLiteSerializer(read_only=True)
	persona = Servidumbre_personaLiteSerializer(read_only=True)
	tipo = TipoLiteSerializer(read_only=True)
	grupo_documento = Servidumbre_grupo_documentoLiteSerializer(read_only=True)


	class Meta:
		model = Servidumbre_predio
		fields=('id','expediente', 'persona', 'nombre_direccion', 'tipo', 'grupo_documento')

##Serializer

class Servidumbre_predioGeoSerializer(serializers.HyperlinkedModelSerializer):
	expediente = serializers.SerializerMethodField(read_only=True)
	persona = serializers.SerializerMethodField(read_only=True)
	porcentajedocumentos = serializers.SerializerMethodField(read_only=True)
	georeferencias = serializers.SerializerMethodField(read_only=True)
	tipo = TipoLiteSerializer(read_only=True)
	grupo_documento = Servidumbre_grupo_documentoLiteSerializer(read_only=True)

	class Meta:
		model = Servidumbre_predio
		fields=('id','expediente','persona','nombre_direccion', 'tipo', 'grupo_documento',
		 'porcentajedocumentos','georeferencias')

	def get_georeferencias(self,obj):
		georeferencias=[]
		if Servidumbre_predio_georeferencia.objects.filter(predio__id=obj.id).exists():
			
			#import pdb; pdb.set_trace()
			objs_georeferencias=Servidumbre_predio_georeferencia.objects.filter(predio__id=obj.id).order_by('orden')
			
			for geo in objs_georeferencias:
				georeferencias.append({
					'id':geo.id,
					'orden':geo.orden,
					'latitud':geo.latitud,
					'longitud':geo.longitud,
					})
		return georeferencias
		

	def get_persona(self,obj):
		return obj.persona.nombres+' '+obj.persona.apellidos

	def get_expediente(self,obj):
		return obj.expediente.id

	def get_porcentajedocumentos(self,obj):
		total_documentos = float(Servidumbre_documento.objects.filter(
			grupo_documento__id=obj.grupo_documento.id).count())
		auxiliar =0
		count = 0

		Servidumbredocumento = Servidumbre_documento.objects.filter(grupo_documento__id=obj.grupo_documento.id)

		for doc in Servidumbredocumento:
				
			auxiliar = float (Servidumbre_predio_documento.objects.filter(
			predio__id=obj.id, documento__id =doc.id ).count())

			if (auxiliar>0):
				count = count +1;					


		documentos_cargados = count				
		
		if total_documentos > 0:
			return round((documentos_cargados / total_documentos)*100,2)
		else:
			return 0

class Servidumbre_predioSerializer(serializers.HyperlinkedModelSerializer):
	#expediente = Servidumbre_expedienteLiteSerializer(read_only=True)
	expediente_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Servidumbre_expediente.objects.all())
	expediente_aux = serializers.SerializerMethodField(read_only=True)

	persona_aux = serializers.SerializerMethodField(read_only=True)
	persona_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Servidumbre_persona.objects.all())
	
	tipo = TipoLiteSerializer(read_only=True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo.objects.filter(app='Servidumbre_predio'))
	
	grupo_documento = Servidumbre_grupo_documentoLiteSerializer(read_only=True)
	grupo_documento_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Servidumbre_grupo_documento.objects.all())
	
	porcentajedocumentos = serializers.SerializerMethodField(read_only=True)

	class Meta:
		model = Servidumbre_predio
		fields=('id','expediente_id','expediente_aux','persona_id','persona_aux',
		 'nombre_direccion', 'tipo', 'tipo_id', 'grupo_documento', 'grupo_documento_id',
		 'porcentajedocumentos')

		# validators=[
		# 		serializers.UniqueTogetherValidator(
		# 		queryset=model.objects.all(),
		# 		fields=( 'persona_id','nombre_direccion'),
		# 		message=('La persona no puede estar repetida con la misma direccion.')
		# 		)
		# 		]

	def get_persona_aux(self,obj):
		return obj.persona.nombres+' '+obj.persona.apellidos

	def get_expediente_aux(self,obj):
		return obj.expediente.id

	def get_porcentajedocumentos(self,obj):		

		total_documentos = float(Servidumbre_documento.objects.filter(
			grupo_documento__id=obj.grupo_documento.id).count())
		auxiliar =0
		count = 0

		Servidumbredocumento = Servidumbre_documento.objects.filter(grupo_documento__id=obj.grupo_documento.id)

		for doc in Servidumbredocumento:
				
			auxiliar = float (Servidumbre_predio_documento.objects.filter(
			predio__id=obj.id, documento__id =doc.id ).count())

			if (auxiliar>0):
				count = count +1;					


		documentos_cargados = count				
		
		if total_documentos > 0:
			return round((documentos_cargados / total_documentos)*100,2)
		else:
			return 0



##LiteSerializer
class Servidumbre_predio_documentoLiteSerializer(serializers.HyperlinkedModelSerializer):
	predio = Servidumbre_predioLiteSerializer(read_only=True)
	documento = Servidumbre_documentoLiteSerializer(read_only=True)

	class Meta:
		model = Servidumbre_predio_documento
		fields = ('id', 'predio','documento','archivo', 'nombre')

##Serializer
class Servidumbre_predio_documentoSerializer(serializers.HyperlinkedModelSerializer):
	predio = Servidumbre_predioLiteSerializer(read_only=True)
	predio_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Servidumbre_predio.objects.all())


	documento = Servidumbre_documentoLiteSerializer(read_only=True)
	documento_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Servidumbre_documento.objects.all())

	class Meta:
		model = Servidumbre_predio_documento
		fields=('id','predio','predio_id', 'documento','documento_id', 'archivo', 'nombre')
		# validators=[
		# 		serializers.UniqueTogetherValidator(
		# 		queryset=model.objects.all(),
		# 		fields=( 'predio_','documento_id'),
		# 		message=('El documento no puede estar repetido con el mismo predio.')
		# 		)
		# 		]

class Servidumbre_predio_georeferenciaSerializer(serializers.HyperlinkedModelSerializer):
	predio = serializers.SerializerMethodField(read_only=True)
	predio_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Servidumbre_predio.objects.all())

	class Meta:
		model = Servidumbre_predio_georeferencia
		fields = ('id', 'predio','predio_id','orden','longitud', 'latitud')

	def get_predio(self,obj):	
		return {'id':obj.predio.id,'nombre_direccion':obj.predio.nombre_direccion}

class Servidumbre_predio_georeferenciaWriteSerializer(serializers.HyperlinkedModelSerializer):
	predio_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Servidumbre_predio.objects.all())

	class Meta:
		model = Servidumbre_predio_georeferencia
		fields = ('id','predio_id','orden','longitud', 'latitud')