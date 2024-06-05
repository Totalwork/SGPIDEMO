from django.db import models
from django.db.models.base import Model
from contrato.models import Contrato
from estado.models import Estado
from usuario.models import Usuario
from sinin4.functions import functions, RandomFileName




class CcCronograma(models.Model):
    nombre = models.CharField(max_length=150)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'cronogramacontrato_cronograma'
        ordering=['nombre', 'activo']

    def __unicode__(self):
        return self.nombre


class CcCapitulo(models.Model):
    nombre = models.CharField(max_length=150)
    cronograma = models.ForeignKey(CcCronograma, related_name='cronograma_capitulo', on_delete=models.PROTECT)
    orden = models.IntegerField()

    class Meta:
        db_table = 'cronogramacontrato_capitulo'
        # unique_together = [
        #     ['cronograma', 'nombre'],
        # ]


    def __unicode__(self):
        return self.cronograma.nombre + '->' + self.nombre

    


class CcActividad(models.Model):
    capitulo = models.ForeignKey(CcCapitulo, related_name='capitulo_actividad', on_delete=models.PROTECT)
    orden = models.IntegerField()
    descripcion = models.TextField()
    inicioprogramado = models.NullBooleanField()
    finprogramado = models.NullBooleanField()
    requiereSoporte = models.NullBooleanField()
    soporteObservaciones = models.NullBooleanField()

    class Meta:
        db_table = 'cronogramacontrato_actividad'
        # unique_together = [
        #     ['descripcion', 'capitulo'],
        # ]

    def __unicode__(self):
        return self.capitulo.cronograma.nombre + '=>' + \
        self.capitulo.nombre + ' => ' + self.descripcion


class CcActividadContrato(models.Model):
    actividad = models.ForeignKey(CcActividad, related_name='actividadContrato_actividad',
    on_delete=models.PROTECT)
    contrato = models.ForeignKey(Contrato, related_name='actividadContrato_contrato', 
    on_delete=models.PROTECT)
    inicioprogramado = models.DateField(null=True,blank=True)
    finprogramado = models.DateField(null=True,blank=True)
    inicioejecutado = models.DateField(null=True,blank=True)
    finejecutado = models.DateField(null=True,blank=True)
    estadoinicio = models.ForeignKey(Estado, related_name='actividadContrato_estadoinicio',
    on_delete=models.PROTECT, null=True,blank=True) 
    estadofin = models.ForeignKey(Estado, related_name='actividadContrato_estadofin',
    on_delete=models.PROTECT, null=True,blank=True)
    observaciones = models.CharField(max_length=150,null=True,blank=True)

    class Meta:
        db_table = 'cronogramacontrato_actividadContrato'
        permissions = (
            ("can_see_cronogramacontrato","can see cronogramacontrato"),
        )

    def __unicode__(self):
        return self.actividad.descripcion


class CcActividadContratoSoporte(models.Model):
    actividadcontrato = models.ForeignKey(CcActividadContrato, 
    related_name='ActividadContratoSoporte_actividadcontrato',
     on_delete=models.PROTECT)
    nombre = models.CharField(max_length=30)
    # archivo = models.FileField(upload_to='cronograma_contrato',null=True)
    archivo = models.FileField(upload_to = RandomFileName(
        'cronograma_contrato','crono_acs'), null=True)

    class Meta:
        db_table = "cronogramacontrato_actividadContratoSoporte"
        # unique_together = [
        #     ['actividadcontrato', 'nombre'],
        # ]


class CcActividadContratoResponsable(models.Model):
    actividadcontrato = models.ForeignKey(CcActividadContrato, 
    related_name='ActividadContratoResponsable_actividadcontrato',
     on_delete=models.PROTECT)
    usuario = models.ForeignKey(Usuario, related_name='ActividadContratoResponsable_actividadcontrato',
    on_delete=models.PROTECT)

    class Meta:
        db_table = "cronogramacontrato_actividadContratoResponsable"
        # unique_together = [
        #     ['actividadcontrato', 'usuario'],
        # ]

    def __unicode__(self):
        return self.id