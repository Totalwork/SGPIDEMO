from .models import *


class PeriodicidadSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = APeriodicidadG
		fields=('id','nombre','numero_dias')

#Api rest para Esquema de Capitulos
class EsquemaCapitulosSerializer(serializers.HyperlinkedModelSerializer):

	tipo=tipoC()
	macrocontrato=ContratoLiteSerializer(read_only=True)
	macrocontrato_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=Contrato.objects.filter(tipo_contrato=tipo.m_contrato))	

	class Meta:
		model = BEsquemaCapitulosG
		fields=('id','macrocontrato','macrocontrato_id','nombre')


#Api rest para Esquema de Capitulos de las actividades
class EsquemaCapitulosActividadesSerializer(serializers.HyperlinkedModelSerializer):

	esquema=EsquemaCapitulosSerializer(read_only=True, required = False)
	esquema_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=BEsquemaCapitulosG.objects.all())	

	
	class Meta:
		model = CEsquemaCapitulosActividadesG
		fields=('id','esquema','esquema_id','nombre','nivel','padre','peso')


class EsquemaCapitulosActividadesLiteSerializer(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model = CEsquemaCapitulosActividadesG
		fields=('id','nombre')


#Api rest para regla de estado
class ReglaEstadoGraficoSerializer(serializers.HyperlinkedModelSerializer):

	esquema=EsquemaCapitulosSerializer(read_only=True)
	esquema_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=BEsquemaCapitulosG.objects.all())

	reglaAnterior=serializers.SerializerMethodField()	

	class Meta:
		model = CReglasEstadoG
		fields=('id','esquema','esquema_id','orden','operador','limite','nombre','reglaAnterior',)

	def get_reglaAnterior(self, obj):
		return CReglasEstadoG.objects.filter(orden__lt=obj.orden,esquema_id=obj.esquema_id).values('id','nombre').order_by('orden').last()


class CronogramaSerializerLite(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Cronograma
		fields = ('id','nombre','fechaInicio','fechaFinal')

class CronogramaSerializer(serializers.HyperlinkedModelSerializer):
	proyecto=ProyectoLite2Serializer(read_only=True)
	proyecto_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=Proyecto.objects.all())	

	# estado=ReglaEstadoGraficoSerializer(read_only=True, allow_null = True)
	# estado_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=CReglasEstadoG.objects.all(),allow_null = True)	

	periodicidad=PeriodicidadSerializer(read_only=True, allow_null = True)
	periodicidad_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=APeriodicidadG.objects.all(),allow_null = True)	

	esquema=EsquemaCapitulosSerializer(read_only=True, allow_null = True)
	esquema_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=BEsquemaCapitulosG.objects.all(),allow_null = True)	

	

	class Meta:
		model = Cronograma
		fields=('id','proyecto','proyecto_id','periodicidad',
			'esquema_id','esquema','periodicidad_id',
			'programacionCerrada','nombre','fechaInicio','fechaFinal')
#Api rest para Detalle Presupuesto

class CatalogoUnidadConstructivaSerializer(serializers.HyperlinkedModelSerializer):
	mcontrato = ContratoLiteSerializer(read_only = True)
	mcontrato_id = serializers.PrimaryKeyRelatedField(read_only=True)
	
	class Meta:
		model=CatalogoUnidadConstructiva
		fields=('id','nombre','ano','activo','mcontrato', 'mcontrato_id')

class TipoUnidadConstructivaSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model=TipoUnidadConstructiva
		fields=('id','nombre','activa')


class UnidadConstructivaLiteSerializer(serializers.HyperlinkedModelSerializer):
	
	catalogo = CatalogoUnidadConstructivaSerializer(read_only=True)
	tipoUnidadConstructiva = TipoUnidadConstructivaSerializer(read_only=True)

	class Meta:
		model=UnidadConstructiva
		fields=('id','catalogo','tipoUnidadConstructiva',
			'codigo','descripcion')

class UnidadConstructivaSerializer(serializers.HyperlinkedModelSerializer):
	catalogo = CatalogoUnidadConstructivaSerializer(read_only=True)
	catalogo_id = serializers.PrimaryKeyRelatedField(read_only=True)

	tipoUnidadConstructiva = TipoUnidadConstructivaSerializer(read_only=True)
	tipoUnidadConstructiva_id = serializers.PrimaryKeyRelatedField(read_only=True)

	totalManoDeObra = serializers.SerializerMethodField()
	totalMateriales = serializers.SerializerMethodField()

	class Meta:
		model=UnidadConstructiva
		fields=('id','catalogo','catalogo_id','tipoUnidadConstructiva','tipoUnidadConstructiva_id',
			'codigo','descripcion','totalManoDeObra','totalMateriales')

	def get_totalManoDeObra(self, obj):	
		total = 0
		##import pdb; pdb.set_trace()
		queryset = DesgloceManoDeObra.objects.filter(
			unidadConstructiva__id=obj.id).values(
			'manoDeObra__valorHora','rendimiento')
		
		if queryset:
			for row in queryset:
				total = float(total) + (float(row['manoDeObra__valorHora']) * float(row['rendimiento']))

		return round(total,2)

	def get_totalMateriales(self,obj):
		total = 0
		##import pdb; pdb.set_trace()
		queryset = DesgloceMaterial.objects.filter(
			unidadConstructiva__id=obj.id).values(
			'material__valorUnitario','cantidad')
		
		if queryset:
			for row in queryset:
				total = float(total) + (float(row['material__valorUnitario']) * float(row['cantidad']))

		return round(total,2)

class UnidadConstructivaSerializerLite(serializers.HyperlinkedModelSerializer):

	tipoUnidadConstructiva = TipoUnidadConstructivaSerializer(read_only=True)
	tipoUnidadConstructiva_id = serializers.PrimaryKeyRelatedField(read_only=True)

	totalManoDeObra = serializers.SerializerMethodField()
	totalMateriales = serializers.SerializerMethodField()

	class Meta:
		model=UnidadConstructiva
		fields=('id','tipoUnidadConstructiva','tipoUnidadConstructiva_id',
			'codigo','descripcion','totalManoDeObra','totalMateriales')

	def get_totalManoDeObra(self, obj):	
		total = 0
		##import pdb; pdb.set_trace()
		queryset = DesgloceManoDeObra.objects.filter(
			unidadConstructiva__id=obj.id).values(
			'manoDeObra__valorHora','rendimiento')
		
		if queryset:
			for row in queryset:
				total = float(total) + (float(row['manoDeObra__valorHora']) * float(row['rendimiento']))

		return round(total,2)

	def get_totalMateriales(self,obj):
		total = 0
		##import pdb; pdb.set_trace()
		queryset = DesgloceMaterial.objects.filter(
			unidadConstructiva__id=obj.id).values(
			'material__valorUnitario','cantidad')
		
		if queryset:
			for row in queryset:
				total = float(total) + (float(row['material__valorUnitario']) * float(row['cantidad']))

class MaterialSerializer(serializers.HyperlinkedModelSerializer):
	
	catalogo = CatalogoUnidadConstructivaSerializer(read_only=True)
	catalogo_id = serializers.PrimaryKeyRelatedField(read_only=True)

	class Meta:
		model=Material
		fields=('id','codigo','descripcion','valorUnitario', 'unidadMedida', 'catalogo_id', 'catalogo')

class MaterialSerializerLite(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model=Material
		fields=('id','descripcion','codigo')

class MaterialSerializerLite2(serializers.HyperlinkedModelSerializer):

	class Meta:
		model=Material
		fields=('id','codigo','descripcion','valorUnitario', 'unidadMedida')


class DesgloceMaterialSerializer(serializers.HyperlinkedModelSerializer):
	
	material = MaterialSerializer(read_only=True)
	material_id = serializers.PrimaryKeyRelatedField(read_only=True)

	unidadConstructiva = UnidadConstructivaSerializer(read_only=True)
	unidadConstructiva_id = serializers.PrimaryKeyRelatedField(read_only=True)

	class Meta:
		model=DesgloceMaterial
		fields=('id','cantidad','material', 'material_id','unidadConstructiva','unidadConstructiva_id')	


class ManoObraSerializer(serializers.HyperlinkedModelSerializer):
	
	catalogo = CatalogoUnidadConstructivaSerializer(read_only=True)
	catalogo_id = serializers.PrimaryKeyRelatedField(read_only=True)

	class Meta:
		model=ManoDeObra
		fields=('id','codigo','descripcion','valorHora', 'catalogo_id', 'catalogo')

class ManoObraSerializerLite2(serializers.HyperlinkedModelSerializer):

	class Meta:
		model=ManoDeObra
		fields=('id','codigo','descripcion','valorHora')		

class ManoObraSerializerLite(serializers.HyperlinkedModelSerializer):
	
	class Meta:
		model=ManoDeObra
		fields=('id','codigo','descripcion')

class DesgloceManoDeObraSerializer(serializers.HyperlinkedModelSerializer):
	
	manoDeObra = ManoObraSerializer(read_only=True)
	manoDeObra_id = serializers.PrimaryKeyRelatedField(read_only=True)

	unidadConstructiva = UnidadConstructivaSerializer(read_only=True)
	unidadConstructiva_id = serializers.PrimaryKeyRelatedField(read_only=True)

	class Meta:
		model=DesgloceManoDeObra
		fields=('id','rendimiento','manoDeObra', 'manoDeObra_id','unidadConstructiva','unidadConstructiva_id')

#Api rest para Presupuesto
class PresupuestoGraficoSerializer(serializers.HyperlinkedModelSerializer):

	cronograma=CronogramaSerializer(read_only=True)
	cronograma_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=Cronograma.objects.all())	


	class Meta:
		model = EPresupuesto
		fields=('id','cronograma','cronograma_id','cerrar_presupuesto','nombre','aiu')

class DetallePresupuestoGraficoSerializer(serializers.HyperlinkedModelSerializer):

	presupuesto=PresupuestoGraficoSerializer(read_only=True)
	presupuesto_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=EPresupuesto.objects.all())	

	actividad=EsquemaCapitulosActividadesSerializer(read_only=True)
	actividad_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=CEsquemaCapitulosActividadesG.objects.all())

	catalogoUnidadConstructiva = CatalogoUnidadConstructivaSerializer(read_only=True)
	catalogoUnidadConstructiva_id=serializers.PrimaryKeyRelatedField(write_only=True,
		queryset=CatalogoUnidadConstructiva.objects.all())
	sumaPresupuesto=serializers.SerializerMethodField()

	class Meta:
		model = FDetallePresupuesto
		fields=('id','sumaPresupuesto','presupuesto','presupuesto_id',
			'actividad',
			'actividad_id','codigoUC','descripcionUC','valorManoObra','valorMaterial',
			'valorGlobal','cantidad','porcentaje','nombre_padre',
			'catalogoUnidadConstructiva','catalogoUnidadConstructiva_id')


	def get_sumaPresupuesto(self, obj):
		sumatoria=0
		suma=FDetallePresupuesto.objects.filter(presupuesto_id=obj.presupuesto.id)	
		valor=0
		for item in suma:
			valor=float(item.valorMaterial)+float(item.valorManoObra)
			total=valor*float(item.cantidad)

			sumatoria=sumatoria+total

		return round(sumatoria,3)
		
class DetallePresupuestoGraficoLiteSerializer(serializers.HyperlinkedModelSerializer):
	actividad=EsquemaCapitulosActividadesLiteSerializer(read_only=True)
	actividad_id=serializers.PrimaryKeyRelatedField(write_only=True,queryset=CEsquemaCapitulosActividadesG.objects.all())

	sumaPresupuesto=serializers.SerializerMethodField()

	class Meta:
		model = FDetallePresupuesto
		fields=('id','sumaPresupuesto','actividad','actividad_id','codigoUC','descripcionUC',
		'valorGlobal','cantidad','nombre_padre')


	def get_sumaPresupuesto(self, obj):
		sumatoria=0
		suma=FDetallePresupuesto.objects.filter(presupuesto_id=obj.presupuesto.id)	
		valor=0
		for item in suma:
			valor=float(item.valorMaterial)+float(item.valorManoObra)
			total=valor*float(item.cantidad)

			sumatoria=sumatoria+total

		return round(sumatoria,3)



