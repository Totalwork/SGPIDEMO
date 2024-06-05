
from .models import Categoria, Tipo_Activo, Activo, Atributo, Activo_atributo, Activo_atributo_soporte, Activo_persona, Activo_gps, Motivo, Mantenimiento, Soporte_mantenimiento
from contrato.models import Contrato
from parametrizacion.models import Funcionario
from usuario.models import Persona
from rest_framework import serializers


from contrato.views import ContratoLiteSerializerByDidi
from parametrizacion.views import FuncionarioSerializer
from usuario.views import PersonaLiteSerializer

class CategoriaSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Categoria
		fields = ('id','nombre')

		

class Tipo_ActivoSerializer(serializers.HyperlinkedModelSerializer):
	categoria = CategoriaSerializer (read_only=True)
	class Meta:
		model = Tipo_Activo
		fields = ('id','categoria','nombre','prefijo')
		
class Tipo_ActivoLiteSerializer(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model = Tipo_Activo
		fields = ('id','nombre')
		


class ActivoSerializer(serializers.HyperlinkedModelSerializer):
	tipo  =  Tipo_ActivoSerializer (read_only=True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo_Activo.objects.all())

	contrato = ContratoLiteSerializerByDidi (read_only=True)
	contrato_id =  serializers.PrimaryKeyRelatedField(write_only=True, queryset = Contrato.objects.all())

	responsable = FuncionarioSerializer (read_only=True)
	responsable_id =  serializers.PrimaryKeyRelatedField(write_only=True, queryset = Funcionario.objects.all())

	class Meta:
		model = Activo
		fields = ('id','tipo','tipo_id','identificacion','serial_placa','descripcion','contrato','contrato_id','valor_compra','responsable','responsable_id','vida_util_dias','periodicidad_mantenimiento'
			,'debaja','motivo_debaja','soportedebaja','fecha_baja','fecha_alta')
		
class ActivoLiteSerializer(serializers.HyperlinkedModelSerializer):
	tipo  = Tipo_ActivoLiteSerializer (read_only=True)
	contrato = ContratoLiteSerializerByDidi(read_only=True)
	responsable = FuncionarioSerializer (read_only=True)

	class Meta:
		model = Activo
		fields = ('id','tipo','descripcion','identificacion','serial_placa','contrato','valor_compra','responsable','vida_util_dias','periodicidad_mantenimiento'
			,'debaja','motivo_debaja','soportedebaja','fecha_baja','fecha_alta')

class ActivoLite2Serializer(serializers.HyperlinkedModelSerializer):
	tipo_id =  serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo_Activo.objects.all())
	contrato_id =  serializers.PrimaryKeyRelatedField(write_only=True, queryset = Contrato.objects.all())
	responsable_id =  serializers.PrimaryKeyRelatedField(write_only=True, queryset = Funcionario.objects.all())

	num_contrato = serializers.SerializerMethodField(read_only=True)
	tipo = serializers.SerializerMethodField(read_only=True)

	class Meta:
		model = Activo
		fields = ('id','tipo_id','identificacion','serial_placa','descripcion','contrato_id','valor_compra','responsable_id',
			'vida_util_dias','periodicidad_mantenimiento','fecha_alta','tipo','num_contrato')
	
	def get_tipo(self,obj):
		var_return = []
		if obj.tipo:
			var_return = {'nombre':obj.tipo.nombre,'categoria':obj.tipo.categoria.nombre}		
		
		return var_return

	def get_num_contrato(self,obj):
		if obj.contrato:
			return obj.contrato.numero
		else:
			return False



class ActivoLite3Serializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Activo
		fields = ('id','debaja','motivo_debaja','soportedebaja','fecha_baja')

class ActivoLite4Serializer(serializers.HyperlinkedModelSerializer):
	tipo  =  Tipo_ActivoSerializer (read_only=True)
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo_Activo.objects.all())

	contrato = ContratoLiteSerializerByDidi (read_only=True)
	contrato_id =  serializers.PrimaryKeyRelatedField(write_only=True, queryset = Contrato.objects.all())

	responsable = FuncionarioSerializer (read_only=True)
	responsable_id =  serializers.PrimaryKeyRelatedField(write_only=True, queryset = Funcionario.objects.all())

	class Meta:
		model = Activo
		fields = ('id','tipo','tipo_id','identificacion','serial_placa','descripcion','contrato','contrato_id','valor_compra','responsable','responsable_id',
			'vida_util_dias','periodicidad_mantenimiento','motivo_debaja','soportedebaja')

class AtributoSerializer(serializers.HyperlinkedModelSerializer):
	tipo = Tipo_ActivoLiteSerializer (read_only=True)
	class Meta:
		model = Atributo
		fields = ('id','tipo','nombre','requiere_soporte')
		
class AtributoLiteSerializer(serializers.HyperlinkedModelSerializer):
	tipo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo_Activo.objects.all())
	class Meta:
		model = Atributo
		fields = ('id','tipo_id','nombre','requiere_soporte')
		

class Activo_atributoSerializer(serializers.HyperlinkedModelSerializer):
	activo = ActivoLite2Serializer(read_only=True)
	atributo = AtributoLiteSerializer(read_only=True)

	class Meta:
		model = Activo_atributo
		fields = ('id','activo','atributo','valor')
		
class Activo_atributoLiteSerializer(serializers.HyperlinkedModelSerializer):
	activo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Activo.objects.all())
	atributo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Atributo.objects.all())

	activo = ActivoLite2Serializer(read_only=True)
	atributo = AtributoLiteSerializer(read_only=True)

	class Meta:
		model = Activo_atributo
		fields = ('id','activo_id','activo','atributo_id','atributo','valor')
		
class Activo_atributoLite2Serializer(serializers.HyperlinkedModelSerializer):
	

	class Meta:
		model = Activo_atributo
		fields = ('id','valor')



class Activo_atributo_soporteSerializer(serializers.HyperlinkedModelSerializer):
	activo_atributo = Activo_atributoLiteSerializer (read_only=True)

	class Meta:
		model = Activo_atributo_soporte
		fields = ('id','activo_atributo','documento')
		
class Activo_atributo_soporteLiteSerializer(serializers.HyperlinkedModelSerializer):
	activo_atributo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Activo_atributo.objects.all())
	class Meta:
		model = Activo_atributo_soporte
		fields = ('id','activo_atributo_id','documento')

class Activo_atributo_soporteLite2Serializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Activo_atributo_soporte
		fields = ('id','documento')


class Activo_personaSerializer(serializers.HyperlinkedModelSerializer):
	persona = PersonaLiteSerializer(read_only=True)
	activo =  ActivoLite2Serializer (read_only=True)

	class Meta:
		model = Activo_persona
		fields = ('id','persona','activo')
		
class Activo_personaLiteSerializer(serializers.HyperlinkedModelSerializer):
	persona_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Persona.objects.all())
	activo_id =  serializers.PrimaryKeyRelatedField(write_only=True, queryset = Activo.objects.all())

	class Meta:
		model = Activo_persona
		fields = ('id','persona_id','activo_id')
		

class MotivoSerializer(serializers.HyperlinkedModelSerializer):
	tipo_activo = Tipo_ActivoLiteSerializer(read_only=True)

	class Meta:
		model = Motivo
		fields = ('id','tipo_activo','nombre')
		
class MotivoLiteSerializer(serializers.HyperlinkedModelSerializer):
	tipo_activo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Tipo_Activo.objects.all())

	class Meta:
		model = Motivo
		fields = ('id','tipo_activo_id','nombre')
		


class MantenimientoSerializer(serializers.HyperlinkedModelSerializer):
	activo = ActivoLite2Serializer (read_only=True)
	motivo = MotivoLiteSerializer(read_only=True)
	contrato = ContratoLiteSerializerByDidi(read_only=True)

	class Meta:
		model = Mantenimiento
		fields = ('id','activo','motivo','fecha','hora','observaciones','contrato')
		
class MantenimientoLiteSerializer(serializers.HyperlinkedModelSerializer):
	activo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Activo.objects.all())
	motivo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Motivo.objects.all())
	contrato_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Contrato.objects.all())

	class Meta:
		model = Mantenimiento
		fields = ('id','activo_id','motivo_id','fecha','hora','observaciones','contrato_id')
		



class Soporte_mantenimientoSerializer(serializers.HyperlinkedModelSerializer):
	mantenimiento = MantenimientoLiteSerializer(read_only=True)

	class Meta:
		model = Soporte_mantenimiento
		fields = ('id','mantenimiento','nombre','archivo')
		
class Soporte_mantenimientoLiteSerializer(serializers.HyperlinkedModelSerializer):
	mantenimiento_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Mantenimiento.objects.all())

	class Meta:
		model = Soporte_mantenimiento
		fields = ('id','mantenimiento_id','nombre','archivo')
		


class Puntos_gpsSerializer(serializers.HyperlinkedModelSerializer):
	activo = ActivoLite2Serializer(read_only=True)

	class Meta:
		model = Activo_gps
		fields = ('id','activo', 'nombre','longitud','latitud')
		
class Puntos_gpsLiteSerializer(serializers.HyperlinkedModelSerializer):
	activo_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset = Activo.objects.all())

	class Meta:
		model = Activo_gps
		fields = ('id','activo_id','nombre','longitud','latitud')

class Puntos_gpsLite2Serializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Activo_gps
		fields = ('id','nombre','longitud','latitud')


