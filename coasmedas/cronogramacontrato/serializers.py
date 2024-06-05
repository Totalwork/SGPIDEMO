# -*- coding: utf-8 -*-
from django.db.models import Q, query
from rest_framework import viewsets, serializers
from rest_framework.response import Response

from cronogramacontrato.models import CcCronograma, CcCapitulo, CcActividad, CcActividadContrato, CcActividadContratoSoporte, CcActividadContratoResponsable
from contrato.models import Contrato
from contrato.views import ContratoSerializer, ContratoLiteSerializerByRj
from estado.models import Estado
from estado.views import EstadoSerializer
from usuario.models import Usuario
from usuario.views import UsuarioSerializer



class CronogramaSerializer(serializers.HyperlinkedModelSerializer):
    
    cantidad_capitulos = serializers.SerializerMethodField(read_only=True)
    cantidad_actividades = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CcCronograma
        fields = ('id','nombre', 'activo', 'cantidad_capitulos', 'cantidad_actividades')

    def get_cantidad_capitulos(self,obj):
        capitulos = CcCapitulo.objects.filter(cronograma__id = obj.id).count()
        return capitulos

    
    def get_cantidad_actividades(self,obj):
        actividades = CcActividad.objects.filter(capitulo__cronograma__id = obj.id).count()
        return actividades


class CapituloSerializer(serializers.HyperlinkedModelSerializer):
    cronograma = CronogramaSerializer(read_only = True)
    cronograma_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset = CcCronograma.objects.all()
    )

    cantidad_actividades = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CcCapitulo
        fields = ('id','nombre', 'cronograma', 'cronograma_id', 'orden','cantidad_actividades')
    
    def get_cantidad_actividades(self,obj):
        actividades = CcActividad.objects.filter(capitulo__id = obj.id).count()
        return actividades


class ActividadSerializer(serializers.HyperlinkedModelSerializer):
    capitulo = CapituloSerializer(read_only=True)
    capitulo_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset = CcCapitulo.objects.all()
    )

    

    class Meta:
        model = CcActividad
        fields =('id','capitulo','capitulo_id', 'orden','descripcion', 'inicioprogramado',
        'finprogramado', 'requiereSoporte','soporteObservaciones')
    
    


class ActividadContratoSerializer(serializers.HyperlinkedModelSerializer):
    actividad = ActividadSerializer(read_only=True)
    actividad_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset = CcActividadContrato.objects.all()
    )
    contrato = ContratoLiteSerializerByRj(read_only=True)
    contrato_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset = Contrato.objects.filter(tipo_contrato=12)
    )
    estadoinicio = EstadoSerializer(read_only=True)
    estadoinicio_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset = Estado.objects.filter(app = 'cronogramacontrato_estadoinicio')
    )

    estadofin = EstadoSerializer(read_only=True)
    estadofin_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset = Estado.objects.filter(app = 'cronogramacontrato_estadofin')
    )

    cantidad_soportes = serializers.SerializerMethodField(read_only=True)

    # 'actividad','actividad_id', 
    class Meta:
        model = CcActividadContrato
        fields =('id','actividad', 'actividad_id', 'contrato','contrato_id', 'inicioprogramado',
        'finprogramado', 'inicioejecutado','finejecutado','estadoinicio', 
        'estadoinicio_id', 'estadofin', 'estadofin_id','observaciones', 'cantidad_soportes',)
    

    def get_cantidad_soportes(self,obj):
        capitulos = CcActividadContratoSoporte.objects.filter(actividadcontrato__id = obj.id).count()
        return capitulos


class ActividadContratoSoporteSerializer(serializers.HyperlinkedModelSerializer):
    actividadcontrato = ActividadContratoSerializer(read_only=True)
    actividadcontrato_id = serializers.PrimaryKeyRelatedField(
        write_only = True, queryset = CcActividadContrato.objects.all()
    )

    archivo_nombre = serializers.SerializerMethodField(read_only=True)
    

    class Meta:
        model = CcActividadContratoSoporte
        fields = ('id','actividadcontrato', 'actividadcontrato_id', 'nombre', 'archivo', 'archivo_nombre')

    def get_archivo_nombre(self,obj):
        nombre = CcActividadContratoSoporte.objects.get(id = obj.id)
        return str(nombre.archivo)



class ActividadContratoResponsableSerializer(serializers.HyperlinkedModelSerializer):
    actividadcontrato = ActividadContratoSerializer(read_only=True)
    actividadcontrato_id = serializers.PrimaryKeyRelatedField(
        write_only = True,
        queryset = CcActividadContrato.objects.all()
    )
    usuario = UsuarioSerializer(read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(
        write_only = True,
        queryset = Usuario.objects.all()
    )

    class Meta:
        model = CcActividadContratoResponsable
        fields = ('id','actividadcontrato', 'actividadcontrato_id', 'usuario', 'usuario_id',)
