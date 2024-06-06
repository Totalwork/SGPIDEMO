# -*- coding: utf-8 -*-
from contrato.enumeration import estadoC
import json
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.db import transaction
from contrato.models import Contrato
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.db.models import Q, Count, query
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from coasmedas.functions import functions
from cronogramacontrato.models import CcCronograma, CcCapitulo, CcActividad, CcActividadContrato, CcActividadContratoSoporte, CcActividadContratoResponsable
from cronogramacontrato.serializers import CronogramaSerializer, CapituloSerializer, ActividadSerializer, ActividadContratoSerializer, ActividadContratoSoporteSerializer, ActividadContratoResponsableSerializer
from contrato.models import EmpresaContrato
from tipo.models import Tipo
from contrato.views import ContratoCronogramaSerializer, ContratoLiteSerializerByJs, contrato, Empresa_contratoConsultaSerializer
from logs.models import Logs, Acciones
from estado.models import Estado
from datetime import datetime, timedelta


class CronogramaCViewSet(viewsets.ModelViewSet):
    model=CcCronograma
    queryset = model.objects.all()
    serializer_class = CronogramaSerializer
    nombre_modulo='cronogramacontrato.CronogramaC'
    paginate_by = 10

    def retrieve(self,request,*args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({'message':'','status':'success','data':serializer.data})
        except Exception as e:
            functions.toLog(e,self.nombre_modulo)
            return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = super(CronogramaCViewSet, self).get_queryset()
            dato = self.request.query_params.get('dato', None)
            paginacion = self.request.query_params.get('sin_paginacion', None)
            nombre = request.query_params.get('nombre', None)
            filterbyname = request.query_params.get('filterbyname', None)
            sin_paginacion= self.request.query_params.get('sin_paginacion',None)
            if filterbyname:
                if nombre:
                    try:
                        nombre = Q(nombre__contains=nombre)
                        queryCronograma = CcCronograma.objects.filter(nombre)
                        serializer = self.get_serializer(queryCronograma,many=True, context={'request': request,})

                        if queryCronograma.count() > 0:
                            if sin_paginacion is None:
                                page = self.paginate_queryset(queryCronograma)
                                if page is not None:
                                    serializer = self.get_serializer(
                                    page,
                                    many=True, 
                                    context={'request': request,}
							    )
                                return self.get_paginated_response(
								{'message':'','success':'ok',
								'data':serializer.data})
            
                        else:
                            return Response({"message": "Debe pasar el nombre", "success": "error", "data": ''})
                    except Exception as e:
                        functions.toLog(e,'cronogramaContrato list cronograma filterbyname')
                        return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if dato:
                qset=(Q(nombre__icontains=dato) | 
                Q(activo__icontains=dato))

                queryset = self.model.objects.filter(qset)
			
            if paginacion is None:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page,many=True)
                    return self.get_paginated_response({'message':'','success':'ok',
				'data':serializer.data})
			
            serializer = self.get_serializer(queryset,many=True)
            return Response({'message':'','success':'ok',
				'data':serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            functions.toLog(e,self.nombre_modulo)
            return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request, *args, **kwargs):
        if request.method == 'POST':
            try:
                serializer = self.serializer_class(data=request.data,context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_crear, 
                    nombre_modelo='cronogramacontrato.cronograma', 
                    id_manipulado=serializer.data['id'])
                    logs_model.save()
                    
                    return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
                else:
                    return Response({'message':'no se pudo realizar el registro','success':'error',
						'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            try:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer = self.serializer_class(instance, data=request.data, context={'request': request}, partial=partial)
                if serializer.is_valid():
                    serializer.save()
                    logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_actualizar, 
                    nombre_modelo='cronogramacontrato.cronograma', 
                    id_manipulado=serializer.data['id'])
                    logs_model.save()
                    return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
                else:
                    return Response({'message':'no se pudo realizar el registro','success':'error',
						'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

    
    def destroy(self, request, *args, **kwargs):
        if request.method == 'DELETE':
            try:
                instance = self.get_object()
                id_aux = instance.id
                self.perform_destroy(instance)
                logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_borrar, 
                    nombre_modelo='cronogramacontrato.cronograma', 
                    id_manipulado=id_aux)
                logs_model.save()

                return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_202_ACCEPTED)
            
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			    'data':''},status=status.HTTP_400_BAD_REQUEST)


class CapituloViewSet(viewsets.ModelViewSet):
    model=CcCapitulo
    queryset = model.objects.all()
    serializer_class = CapituloSerializer
    nombre_modulo='cronogramacontrato.Capitulo'
    paginate_by = 10

    

    def retrieve(self,request,*args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({'message':'','status':'success','data':serializer.data})
        except Exception as e:
            functions.toLog(e,self.nombre_modulo)
            return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = super(CapituloViewSet, self).get_queryset()
            dato = self.request.query_params.get('dato', None)
            paginacion = self.request.query_params.get('sin_paginacion', None)
            filterbyid = self.request.query_params.get('filterbyid', None)
            cronograma_id = self.request.query_params.get('cronograma_id', None)
            sin_paginacion= self.request.query_params.get('sin_paginacion',None)
            nombre = request.query_params.get('nombre', None)
            filterbyname = request.query_params.get('filterbyname', None)
            #import pdb; pdb.set_trace()

            if filterbyname:
                if nombre:
                    try:
                        nombre = (Q(nombre__contains=nombre) & Q(cronograma_id = cronograma_id))
                        queryCapitulo = CcCapitulo.objects.filter(nombre)
                        serializer = self.get_serializer(queryCapitulo,many=True, context={'request': request,})

                        if queryCapitulo.count() > 0:
                            if sin_paginacion is None:
                                page = self.paginate_queryset(queryCapitulo)
                                if page is not None:
                                    serializer = self.get_serializer(
                                    page,
                                    many=True, 
                                    context={'request': request,}
							    )
                                filterbyname = None
                                return self.get_paginated_response(
								{'message':'','success':'ok',
								'data':serializer.data})
            
                        else:
                            return Response({"message": "Debe pasar el nombre", "success": "error", "data": ''})
                    except Exception as e:
                        functions.toLog(e,'cronogramaContrato list cronograma filterbyname')
                        return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


            if filterbyid:
                try:
                    querysetCapitulos = CcCapitulo.objects.filter(cronograma__id=cronograma_id)

                    if querysetCapitulos.count() > 0:
                        
                        serializer = self.get_serializer(querysetCapitulos,many=True, context={'request': request,})
                        if sin_paginacion is None:
                            page = self.paginate_queryset(querysetCapitulos)
                            if page is not None:
                                serializer = self.get_serializer(
                                    page,
                                    many=True, 
                                    context={'request': request,}
							    )
                                return self.get_paginated_response(
								{'message':'','success':'ok',
								'data':serializer.data})
                        # return Response({'message':'','success':'ok','data':serializer.data})
                    
                    else:
                       return Response({'message':'No se encontraron registros para el id: '+cronograma_id,'success':'ok','data':''}) 

                except Exception as e:
                    functions.toLog(e,'cronogramaContrato')
                    return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                




            if dato:
                qset=(Q(nombre__icontains=dato) | 
                Q(cronograma__icontains=dato) |
                Q(orden__icontains=dato))

                queryset = self.model.objects.filter(qset)
			
            if paginacion is None:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page,many=True)
                    return self.get_paginated_response({'message':'','success':'ok',
				'data':serializer.data})
			
            serializer = self.get_serializer(queryset,many=True)
            return Response({'message':'','success':'ok',
				'data':serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            functions.toLog(e,self.nombre_modulo)
            return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request, *args, **kwargs):
        if request.method == 'POST':
            try:
                # import pdb; pdb.set_trace()
                serializer = self.serializer_class(data=request.data,context={'request': request})
                if serializer.is_valid():
                    #verificar que no exista otro nombre con el mismo cronograma:
                    queryset = CcCapitulo.objects.filter(
                        cronograma__id=request.data['cronograma_id'],
                        nombre=request.data['nombre']
                    )
                    if queryset.count() == 0:
                        serializer.save(cronograma_id=request.data['cronograma_id'])

                        logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_crear, 
                            nombre_modelo='cronogramacontrato.capitulo', 
                            id_manipulado=serializer.data['id'])
                        logs_model.save()
                    
                        return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
    						'data':serializer.data},status=status.HTTP_201_CREATED)
                    else:
                        return Response({'message':'no se pudo guardar el registro porque el capitulo [' + 
                            request.data['nombre'] + '] ya existe en el cronograma', 'success':'error',
                            'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)                        
                else:
                    return Response({'message':'no se pudo realizar el registro','success':'error',
						'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            try:
                # import pdb; pdb.set_trace()
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer = self.serializer_class(instance, data=request.data, context={'request': request}, partial=partial)
                if serializer.is_valid():
                    serializer.save(cronograma_id=request.data['cronograma_id'])
                    logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_actualizar, 
                            nombre_modelo='cronogramacontrato.capitulo', 
                            id_manipulado=serializer.data['id'])
                    logs_model.save()

                    return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
                else:
                    return Response({'message':'no se pudo realizar el registro','success':'error',
						'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

    
    def destroy(self, request, *args, **kwargs):
        if request.method == 'DELETE':
            try:
                # import pdb; pdb.set_trace()
                instance = self.get_object()
                id_aux = instance.id
                self.perform_destroy(instance)
                
                logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_borrar, 
                            nombre_modelo='cronogramacontrato.capitulo', 
                            id_manipulado=id_aux)
                logs_model.save()


                return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_202_ACCEPTED)
            
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			    'data':''},status=status.HTTP_400_BAD_REQUEST)


class ActividadCViewSet(viewsets.ModelViewSet):
    model=CcActividad
    queryset = model.objects.all()
    serializer_class = ActividadSerializer
    nombre_modulo='cronogramacontrato.Actividad'
    paginate_by = 10

    def retrieve(self,request,*args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({'message':'','status':'success','data':serializer.data})
        except Exception as e:
            functions.toLog(e,self.nombre_modulo)
            return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = super(ActividadCViewSet, self).get_queryset()
            dato = self.request.query_params.get('dato', None)
            paginacion = self.request.query_params.get('sin_paginacion', None)
            
            nombre = request.query_params.get('nombre', None)
            filterbyname = request.query_params.get('filterbyname', None)
            listbyid = self.request.query_params.get('listbyid',None)
            capituloid = self.request.query_params.get('capituloid',None)

            if filterbyname:
                if nombre:
                    try:
                        nombre = (Q(descripcion__contains=nombre) & Q(capitulo_id = capituloid))
                        queryActividad = CcActividad.objects.filter(nombre)
                        serializer = self.get_serializer(queryActividad,many=True, context={'request': request,})

                        if queryActividad.count() > 0:
                            if paginacion is None:
                                page = self.paginate_queryset(queryActividad)
                                if page is not None:
                                    serializer = self.get_serializer(
                                    page,
                                    many=True, 
                                    context={'request': request,}
							    )
                                filterbyname = None
                                return self.get_paginated_response(
								{'message':'','success':'ok',
								'data':serializer.data})
            
                        else:
                            return Response({"message": "Debe pasar el nombre", "success": "error", "data": ''})
                    except Exception as e:
                        functions.toLog(e,'cronogramaContrato list cronograma filterbyname')
                        return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


            # import pdb; pdb.set_trace()
            if listbyid:
                #import pdb; pdb.set_trace()
                try:
                    querysetActividades = CcActividad.objects.filter(
                        capitulo__id = capituloid
                    )

                    if querysetActividades.count() > 0:
                        serializer = self.get_serializer(querysetActividades,many=True, context={'request': request,})
                        if paginacion is None:
                            page = self.paginate_queryset(querysetActividades)
                            if page is not None:
                                serializer = self.get_serializer(page,many=True, context={'request': request,})
                                return self.get_paginated_response({'message':'','success':'ok',
				                    'data':serializer.data})
                        #return Response({'message':'','success':'ok','data':serializer.data, 'count': querysetActividades.count()})
                
                    else:
                        return Response({'message':'No se encontraron registros para el id: '+capituloid,'success':'ok','data':''})
                
                except Exception as e:
                    functions.toLog(e,'cronogramaContrato')
                    return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)






            if dato:
                qset=(Q(capitulo__icontains=dato) | 
                Q(orden__icontains=dato) |
                Q(descripcion__icontains=dato) |
                Q(inicioprogramado__icontains=dato) |
                Q(finprogramado__icontains=dato) |
                Q(requiereSoporte__icontains=dato) |
                Q(soporteObservaciones__icontains=dato)
                )

                queryset = self.model.objects.filter(qset)
			
            if paginacion is None:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page,many=True)
                    return self.get_paginated_response({'message':'','success':'ok',
				'data':serializer.data})
			
            serializer = self.get_serializer(queryset,many=True)
            return Response({'message':'','success':'ok',
				'data':serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            functions.toLog(e,self.nombre_modulo)
            return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request, *args, **kwargs):
        if request.method == 'POST':
            try:
                #import pdb; pdb.set_trace()
                serializer = self.serializer_class(data=request.data,context={'request': request})
                if serializer.is_valid():
                    queryset = CcActividad.objects.filter(
                        capitulo_id = request.data['capitulo_id'],
                        descripcion = request.data['descripcion']
                    )

                    if queryset.count() == 0:
                        #import pdb; pdb.set_trace()
                        serializer.save(capitulo_id = int(request.data['capitulo_id']))
                        logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_crear, 
                            nombre_modelo='cronogramacontrato.actividad', 
                            id_manipulado=serializer.data['id'])
                        logs_model.save()
                        id_cronograma = serializer.data['capitulo']['cronograma']['id']
                        queryActividadContrato = CcActividadContrato.objects.filter(actividad__capitulo__cronograma_id = id_cronograma).values('contrato__id').distinct()
                        for item in queryActividadContrato:
                            queryAsociacion = CcActividadContrato(contrato_id=item['contrato__id'], actividad_id=serializer.data['id'])
                            queryAsociacion.save()
                            logs_model_asociar=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_crear, 
                            nombre_modelo='cronogramacontrato.actividad.asociarcronograma', 
                            id_manipulado=queryAsociacion.id)
                            logs_model_asociar.save()
                        
                        


                        return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						    'data':serializer.data},status=status.HTTP_201_CREATED)
                    
                    else:
                        return Response({'message':'no se pudo realizar el registro porque el capitulo ['+ request.data['capitulo_id'] 
                        + '] ya existe y/o está relacionado con la descripcion [' + request.data['descripcion'] +']','success':'error',
                            'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)


                else:
                    return Response({'message':'no se pudo realizar el registro','success':'error',
						'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            try:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer = self.serializer_class(instance, data=request.data, context={'request': request}, partial=partial)
                if serializer.is_valid():
                    serializer.save(capitulo_id = int(request.data['capitulo_id']))

                    logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_actualizar, 
                            nombre_modelo='cronogramacontrato.actividad', 
                            id_manipulado=serializer.data['id'])
                    logs_model.save()

                    return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
                else:
                    return Response({'message':'no se pudo realizar el registro','success':'error',
						'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

    
    def destroy(self, request, *args, **kwargs):
        if request.method == 'DELETE':
            try:
                instance = self.get_object()
                id_aux = instance.id
                self.perform_destroy(instance)

                logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_borrar, 
                            nombre_modelo='cronogramacontrato.actividad', 
                            id_manipulado=id_aux)
                logs_model.save()


                return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_202_ACCEPTED)
            
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			    'data':''},status=status.HTTP_400_BAD_REQUEST)


class ActividadContratoViewSet(viewsets.ModelViewSet):
    model=CcActividadContrato
    queryset = model.objects.all()
    serializer_class = ActividadContratoSerializer
    nombre_modulo='cronogramacontrato.ActividadContrato'
    paginate_by = 10

    def retrieve(self,request,*args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({'message':'','status':'success','data':serializer.data})
        except Exception as e:
            functions.toLog(e,self.nombre_modulo)
            return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = super(ActividadContratoViewSet, self).get_queryset()
            dato = self.request.query_params.get('dato', None)
            paginacion = self.request.query_params.get('sin_paginacion', None)

            listbyid = self.request.query_params.get('listbyid',None)
            id_contrato = self.request.query_params.get('idcontrato',None)
            #import pdb; pdb.set_trace()
            if listbyid:
                try:

                    querysetContrato = CcActividadContrato.objects.filter(
                        contrato__id = id_contrato
                    )

                    if querysetContrato.count() > 0:
                        serializer = self.get_serializer(querysetContrato,many=True, context={'request': request,}) # Usar serializador lite
                        # datos = querysetContrato.values()
                        return Response({'message':'','success':'ok','data':serializer.data})
                    
                    else:
                        return Response({'message':'No se encontraron registros para el id: '+id_contrato,'success':'ok','data':''})
                    

                except Exception as e:
                    functions.toLog(e,'cronogramaContrato')
                    return Response({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                

            if dato:
                qset=(Q(actividad__icontains=dato) | 
                Q(contrato__icontains=dato) |
                Q(inicioprogramado__icontains=dato) |
                Q(finprogramado__icontains=dato) |
                Q(inicioejecutado__icontains=dato) |
                Q(finejecutado__icontains=dato) |
                Q(estadoinicio__icontains=dato) |
                Q(estadofin__icontains=dato) |
                Q(soportes__icontains=dato) |
                Q(observaciones__icontains=dato) |
                Q(cantidad_soportes__icontains=dato)
                )

                queryset = self.model.objects.filter(qset)
			
            if paginacion is None:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page,many=True)
                    return self.get_paginated_response({'message':'','success':'ok',
				'data':serializer.data})
			
            serializer = self.get_serializer(queryset,many=True)
            return Response({'message':'','success':'ok',
				'data':serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            functions.toLog(e,self.nombre_modulo)
            return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request, *args, **kwargs):
        if request.method == 'POST':
            try:
                #import pdb; pdb.set_trace()
                serializer = self.serializer_class(data=request.data,context={'request': request})
                if serializer.is_valid():
                    queryset = CcActividadContrato.objects.filter(
                        actividad_id = request.data['actividad_id'],
                        contrato_id = request.data['contrato_id']
                    )

                    if queryset.count() == 0:
                        serializer.save(actividad_id = int(request.data['actividad_id']),
                        contrato_id = int(request.data['contrato_id']),
                        estadoinicio_id = request.data['estadoinicio_id'],
                        estadofin_id = request.data['estadofin_id']
                        )

                        logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_crear, 
                            nombre_modelo='cronogramacontrato.actividadcontrato', 
                            id_manipulado=serializer.data['id'])
                        logs_model.save()


                        return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)

                    else:
                        return Response({'message':'no se pudo realizar el registro porque la actividad ['+ request.data['actividad_id'] 
                        + '] ya existe y/o está relacionado con el contrato [' + request.data['contrato_id'] +']','success':'error',
                            'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)
                    
                    
                else:
                    return Response({'message':'no se pudo realizar el registro','success':'error',
						'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            try:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer = self.serializer_class(instance, data=request.data, context={'request': request}, partial=partial)
                if serializer.is_valid():
                    serializer.save(actividad_id = int(request.data['actividad_id']),
                        contrato_id = int(request.data['contrato_id']),
                        estadoinicio_id = request.data['estadoinicio_id'],
                        estadofin_id = request.data['estadofin_id']
                        )
                    logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_actualizar, 
                            nombre_modelo='cronogramacontrato.actividadcontrato', 
                            id_manipulado=serializer.data['id'])
                    logs_model.save()
                    return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
                else:
                    return Response({'message':'no se pudo realizar el registro','success':'error',
						'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

    
    def destroy(self, request, *args, **kwargs):
        if request.method == 'DELETE':
            try:
                instance = self.get_object()
                id_aux = instance.id
                self.perform_destroy(instance)

                logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_borrar, 
                            nombre_modelo='cronogramacontrato.actividadcontrato', 
                            id_manipulado=id_aux)
                logs_model.save()

                return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_202_ACCEPTED)
            
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			    'data':''},status=status.HTTP_400_BAD_REQUEST)


class ActividadContratoSoporteViewSet(viewsets.ModelViewSet):
    model=CcActividadContratoSoporte
    queryset = model.objects.all()
    serializer_class = ActividadContratoSoporteSerializer
    nombre_modulo='cronogramacontrato.ActividadContratoSoporte'
    paginate_by = 10

    def retrieve(self,request,*args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({'message':'','status':'success','data':serializer.data})
        except Exception as e:
            functions.toLog(e,self.nombre_modulo)
            return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = super(ActividadContratoSoporteViewSet, self).get_queryset()
            dato = self.request.query_params.get('dato', None)
            paginacion = self.request.query_params.get('sin_paginacion', None)

            if dato:
                qset=(Q(actividadcontrato__icontains=dato) | 
                Q(nombre__icontains=dato) |
                Q(archivo__icontains=dato))

                queryset = self.model.objects.filter(qset)
			
            if paginacion is None:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page,many=True)
                    return self.get_paginated_response({'message':'','success':'ok',
				'data':serializer.data})
			
            serializer = self.get_serializer(queryset,many=True)
            return Response({'message':'','success':'ok',
				'data':serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            functions.toLog(e,self.nombre_modulo)
            return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request, *args, **kwargs):
        if request.method == 'POST':
            try:
                # import pdb; pdb.set_trace()
                serializer = self.serializer_class(data=request.data,context={'request': request})
                if serializer.is_valid():
                    queryset = CcActividadContratoSoporte.objects.filter(
                        actividadcontrato_id = int(request.data['actividadcontrato_id']),
                        nombre = request.data['nombre']
                    )

                    if queryset.count() == 0:
                        serializer.save(
                            actividadcontrato_id = int(request.data['actividadcontrato_id']),
                            archivo=self.request.FILES.get('archivo'))

                        logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_crear, 
                            nombre_modelo='cronogramacontrato.actividadcontratosoporte', 
                            id_manipulado=serializer.data['id'])
                        logs_model.save()
                    
                        return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						    'data':serializer.data},status=status.HTTP_201_CREATED)
                    else:
                        return Response({'message':'no se pudo realizar el registro porque la actividadcontrato_id ['+ request.data['actividadcontrato_id'] 
                        + '] ya existe y/o está relacionado con el nombre [' + request.data['nombre'] +']','success':'error',
                            'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    return Response({'message':'no se pudo realizar el registro','success':'error',
						'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            try:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer = self.serializer_class(
                    instance, 
                    data=request.DATA, 
                    context={'request': request}, 
                    partial=partial)
                if serializer.is_valid():
                    valores=CcActividadContratoSoporte.objects.get(id=instance.id)
                    if self.request.FILES.get('archivo') is not None:
                        serializer.save(
                            actividadcontrato_id = int(request.data['actividadcontrato_id']),
                            archivo = self.request.FILES.get('archivo'))
                    else:
                        serializer.save(
                            actividadcontrato_id = int(request.data['actividadcontrato_id']),
                            archivo = valores.archivo)

                    logs_model = Logs(
                        usuario_id=request.user.usuario.id, 
                        accion=Acciones.accion_actualizar,
                        nombre_modelo='cronogramacontrato.actividadcontratosoporte', 
                        id_manipulado=serializer.data['id'])
                    logs_model.save()


                    return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
                else:
                    print (serializer.errors)
                    return Response({'message':'no se pudo realizar el registro','success':'error',
						'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            id_aux = instance.id
            self.perform_destroy(instance)
            logs_model=Logs(usuario_id=request.user.usuario.id,
                accion=Acciones.accion_borrar,
                nombre_modelo='cronogramacontrato.actividadcontratosoporte', 
                id_manipulado=id_aux)
            logs_model.save()

            return Response({'message':'El registro se ha eliminado correctamente',
                'success':'ok', 'data':''},status=status.HTTP_200_OK)
        
        except Exception as e:
            functions.toLog(e,self.nombre_modulo)
            return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			    'data':''},status=status.HTTP_400_BAD_REQUEST)

 
class ActividadContratoResponsableViewSet(viewsets.ModelViewSet):
    model=CcActividadContratoResponsable
    queryset = model.objects.all()
    serializer_class = ActividadContratoResponsableSerializer
    nombre_modulo='cronogramacontrato.ActividadContratoResponsable'
    paginate_by = 10

    def retrieve(self,request,*args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({'message':'','status':'success','data':serializer.data})
        except Exception as e:
            functions.toLog(e,self.nombre_modulo)
            return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = super(ActividadContratoResponsableViewSet, self).get_queryset()
            dato = self.request.query_params.get('dato', None)
            paginacion = self.request.query_params.get('sin_paginacion', None)

            if dato:
                qset=(Q(actividadcontrato__icontains=dato) | 
                Q(usuario__icontains=dato))

                queryset = self.model.objects.filter(qset)
			
            if paginacion is None:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page,many=True)
                    return self.get_paginated_response({'message':'','success':'ok',
				'data':serializer.data})
			
            serializer = self.get_serializer(queryset,many=True)
            return Response({'message':'','success':'ok',
				'data':serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            functions.toLog(e,self.nombre_modulo)
            return Response({'message':'No se encontraron datos','success':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request, *args, **kwargs):
        if request.method == 'POST':
            try:
                serializer = self.serializer_class(data=request.data,context={'request': request})
                if serializer.is_valid():
                    queryset = CcActividadContratoResponsable.objects.filter(
                        actividadcontrato_id = int(request.data['actividadcontrato_id']),
                        usuario_id = int(request.data['usuario_id'])
                    )


                    if queryset.count() == 0:
                        serializer.save(actividadcontrato_id = int(request.data['actividadcontrato_id']),
                        usuario_id = int(request.data['usuario_id']))

                        logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_crear, 
                            nombre_modelo='cronogramacontrato.actividadcontratoresponsable', 
                            id_manipulado=serializer.data['id'])
                        logs_model.save()


                        return Response({'message':'El registro ha sido guardado exitosamente','success':'ok',
						    'data':serializer.data},status=status.HTTP_201_CREATED)
                    
                    else:
                        return Response({'message':'no se pudo realizar el registro porque la actividadcontrato_id ['+ request.data['actividadcontrato_id'] 
                        + '] ya existe y/o está relacionado con el usuario_id [' + request.data['usuario_id'] +']','success':'error',
                            'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)

                else:
                    return Response({'message':'no se pudo realizar el registro','success':'error',
						'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            try:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer = self.serializer_class(instance, data=request.data, context={'request': request}, partial=partial)
                if serializer.is_valid():
                    serializer.save()

                    logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_actualizar, 
                            nombre_modelo='cronogramacontrato.actividadcontratoresponsable', 
                            id_manipulado=serializer.data['id'])
                    logs_model.save()


                    return Response({'message':'El registro ha sido actualizado exitosamente','success':'ok',
						'data':serializer.data},status=status.HTTP_201_CREATED)
                else:
                    return Response({'message':'no se pudo realizar el registro','success':'error',
						'data':serializer.data},status=status.HTTP_406_NOT_ACCEPTABLE)
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
					'data':''},status=status.HTTP_400_BAD_REQUEST)

    
    def destroy(self, request, *args, **kwargs):
        if request.method == 'DELETE':
            try:
                instance = self.get_object()
                id_aux = instance.id
                self.perform_destroy(instance)

                logs_model=Logs(usuario_id=request.user.usuario.id, accion=Acciones.accion_borrar, 
                        nombre_modelo='cronogramacontrato.actividadcontratoresponsable', 
                        id_manipulado=id_aux)
                logs_model.save()



                return Response({'message':'El registro se ha eliminado correctamente','success':'ok',
				'data':''},status=status.HTTP_202_ACCEPTED)
            
            except Exception as e:
                functions.toLog(e,self.nombre_modulo)
                return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			    'data':''},status=status.HTTP_400_BAD_REQUEST)

def llenarFechas():

    def remover_duplicados(diccionario):
        resultado = []       
        for i in range(len(diccionario)):
            resultado.append(diccionario[i].get('fecha_firma').strftime("%Y"))
        resultadoFinal = []
        for i in resultado:
            if i not in resultadoFinal:
                resultadoFinal.append(i)
        
        
        return resultadoFinal

    try:
        filtrado = Contrato.objects.filter(fecha_firma__isnull=False, tipo_contrato=12)
        fechasSinProcesar =filtrado.values('fecha_firma')
        
        fechasProcesadas =remover_duplicados(fechasSinProcesar)
        return fechasProcesadas
    

    except Exception as e:
            functions.toLog(e,'cronogramacontrato.llenarFechas()')


@login_required
def index_cronogramacontrato(request):
    return render(request, 'cronogramacontrato.html', {})


@login_required
def index_esquemacronograma(request):
    return render(request, 'esquemacronograma.html', {})


@login_required
def index_capitulosesquema(request, id_cronograma=None):
    # return render(request, 'capitulosesquema.html', {})
    return render(request, 'capitulosesquema.html',{'id_cronograma':id_cronograma,'model':'CcCapitulo','app':'cronogramacontrato'})


@login_required
def index_listadoactividades(request, capituloid=None):
    # return render(request, 'listadoactividades.html', {})
    cronograma_id = CcCapitulo.objects.get(id = capituloid).cronograma.id

    return render(request, 'listadoactividades.html',{'capituloid':capituloid, 'id_cronograma':cronograma_id,'model':'CcActividad','app':'cronogramacontrato'})


@login_required
def index_seguimientodelcontrato(request, id_contrato=None):
    # return render(request, 'seguimientodelcontrato.html', {})
    #get el cronograma con el cual se implementa el contrato
    if id_contrato:
        cronogramaContrato = CcActividadContrato.objects.filter(
            contrato__id=id_contrato
            ).first().actividad.capitulo.cronograma

    return render(request, 'seguimientodelcontrato.html',
        {'id_contrato':id_contrato,
        'model':'CcActividadContrato',
        'app':'cronogramacontrato',
        'cronogramaContrato':cronogramaContrato})


@api_view(['GET'])
def activarCronograma(request):
    pass



@api_view(['GET'])
def fillGraphById(request):
    try:
        
        retorno = []
        id = request.query_params.get('id', None)
        qset = Q(empresa__id=request.user.usuario.empresa.id,
         contrato__tipo_contrato__id=12, contrato_id = id)


        querysetContratosConAcceso = EmpresaContrato.objects.filter(
            qset).values_list('contrato__id',flat=True) 


        querysetContratos = Contrato.objects.filter(
            id__in=list(querysetContratosConAcceso))

        queryset = querysetContratos.values('fechaAdjudicacion',
            'fondo__id').order_by('fechaAdjudicacion').distinct()
        
        #calculo de grafica de estado de inicio de actividades
        #import pdb; pdb.set_trace()
        estadoInicioArray=[]
        queryset = CcActividadContrato.objects.filter(
            contrato__id__in=list(querysetContratos.values_list('id', flat=True))).values(
            'estadoinicio__nombre').annotate(total = Count('estadoinicio__nombre'))

        for obj in queryset:
            estadoInicioArray.append([obj['estadoinicio__nombre'],obj['total']])

        retorno.append({
            'nombre' : 'estados de inicio',
            'data': estadoInicioArray
            })
        
        #calculo de grafica de estado de fin de actividades
        #import pdb; pdb.set_trace()
        estadoFinArray=[]
        queryset = CcActividadContrato.objects.filter(
            contrato__id__in=list(querysetContratos.values_list('id', flat=True))).values(
            'estadofin__nombre').annotate(total = Count('estadofin__nombre'))

        for obj in queryset:
            estadoFinArray.append([obj['estadofin__nombre'],obj['total']])

        retorno.append({
            'nombre' : 'estados de fin',
            'data': estadoFinArray
            })


        return Response({"message": "", "success": "ok", "data": retorno})
    except Exception as e:
        functions.toLog(e,'cronogramacontrato.fillGraphById')
        return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
            'data':''},status=status.HTTP_400_BAD_REQUEST) 



@api_view(['GET'])
def fillGraph(request):
    try:
        #import pdb; pdb.set_trace()
        anos = []
        fondos = []
        series = []
        retorno = []
        ano = request.query_params.get('ano', None)
        fondo = request.query_params.get('fondo', None)
        qset = Q(empresa__id=request.user.usuario.empresa.id,
         contrato__tipo_contrato__id=12)

        if fondo:
            qset = qset & Q(contrato__fondo__id=fondo)
        if ano:
            desde = ano + '-01-01'
            hasta = ano + '-12-31'
            qset = qset & Q(contrato__fechaAdjudicacion__range=[desde,hasta])

        querysetContratosConAcceso = EmpresaContrato.objects.filter(
            qset).values_list('contrato__id',flat=True) 


        querysetContratos = Contrato.objects.filter(
            id__in=list(querysetContratosConAcceso))

        queryset = querysetContratos.values('fechaAdjudicacion',
            'fondo__id').order_by('fechaAdjudicacion').distinct()
        for obj in queryset:
            ano =  obj['fechaAdjudicacion'].strftime("%Y")
            if not ano in anos:
                anos.append(
                    ano
                )
            if not obj['fondo__id'] in fondos:
                fondos.append(obj['fondo__id'])

        for fondo in fondos:
            anoFondo = []
            for ano in anos:
                
                qset = Q(fondo__id=fondo)
                desde = ano + '-01-01'
                hasta = ano + '-12-31'
                qset = qset & Q(fecha_firma__range=[desde,hasta])

                queryset = querysetContratos.filter(qset)
                if queryset.count() > 0:
                    data = ContratoCronogramaSerializer(queryset,many=True, 
                        context={'request': request,})

                    #import pdb; pdb.set_trace()                
                    acum = 0
                    for element in data.data:
                        acum = acum + element['avance']

                    anoFondo.append(round(float(acum / queryset.count()),1))
                else:
                    anoFondo.append(0)

            series.append(
                {
                    'name' : Tipo.objects.get(id=fondo).nombre,
                    'data' : anoFondo
                }
            )

        datagrafica = {
            'nombre' : 'avance por contrato',
            'categorias' : anos,
            'series' : series
        }

        retorno.append(datagrafica)   

        #calculo de grafica de estado de inicio de actividades
        
        estadoInicioArray=[]
        queryset = CcActividadContrato.objects.filter(
            contrato__id__in=list(querysetContratos.values_list('id', flat=True))).values(
            'estadoinicio__nombre').annotate(total = Count('estadoinicio__nombre'))

        for obj in queryset:
            estadoInicioArray.append([obj['estadoinicio__nombre'],obj['total']])

        retorno.append({
            'nombre' : 'estados de inicio',
            'data': estadoInicioArray
            })
        
        #calculo de grafica de estado de fin de actividades
        #import pdb; pdb.set_trace()
        estadoFinArray=[]
        queryset = CcActividadContrato.objects.filter(
            contrato__id__in=list(querysetContratos.values_list('id', flat=True))).values(
            'estadofin__nombre').annotate(total = Count('estadofin__nombre'))

        for obj in queryset:
            estadoFinArray.append([obj['estadofin__nombre'],obj['total']])

        retorno.append({
            'nombre' : 'estados de fin',
            'data': estadoFinArray
            })


        return Response({"message": "", "success": "ok", "data": retorno})
    except Exception as e:
        functions.toLog(e,'cronogramacontrato.fillGraph')
        return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
            'data':''},status=status.HTTP_400_BAD_REQUEST) 



@api_view(['GET'])
def getAnosyFondos(request):
    try:
        anos = []
        fondos = []
        querysetContratos = Contrato.objects.filter(
            tipo_contrato__id=12,fechaAdjudicacion__isnull=False)
        queryset = querysetContratos.values('fondo__id','fondo__nombre').distinct()
        for obj in queryset:

            fondo = {
                        'id' : obj['fondo__id'],
                        'nombre' : obj['fondo__nombre']
                    }
            if not fondo in fondos:
                fondos.append(
                    fondo
                )
        #import pdb; pdb.set_trace()
        queryset = querysetContratos.values('fechaAdjudicacion').distinct()
        for obj in queryset:
            ano = {
                'valor': obj['fechaAdjudicacion'].strftime("%Y"), 
                'texto': obj['fechaAdjudicacion'].strftime("%Y")
            }
            if not ano in anos:
                anos.append(
                    ano
                )
        data = {
            'fondos' : fondos,
            'anos' : anos
        }
        return Response({"message": "", "success": "ok", "data": data})

    except Exception as e:
        functions.toLog(e,'cronogramacontrato.getAnosyFondos')
        return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
            'data':''},status=status.HTTP_400_BAD_REQUEST)

#Revisar si aún sigue en uso
@api_view(['GET'])
def getActividadesContratosTablaById(request):
    try:
        # CcActividadContrato
        # import pdb; pdb.set_trace()
        id = request.query_params.get('id', None)
        queryset = CcActividadContrato.objects.filter(
            contrato__id=id, contrato__tipo_contrato=12
        )

        retorno = []
        retorno.append(queryset.values())

        if retorno:
            return Response({"message": "", "success": "ok", "data": retorno[0]})


    
    except Exception as e:
        functions.toLog(e,'cronogramacontrato.getAnosyFondos')
        return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
            'data':''},status=status.HTTP_400_BAD_REQUEST)

# borrar
@api_view(['GET'])
def VerSoporte(request):
    try:
        link = request.query_params.get('link', None)
        return functions.exportarArchivoS3(str(link))

    except Exception as e:
        functions.toLog(e, 'cronogramacontrato.VerSoporte')
        return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
            'data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def CambiarEstadoCronograma(request):
    try:
        id = request.query_params.get('id', None)
        estado = request.query_params.get('estado', None)
        queryCronograma = CcCronograma.objects.get(id=id)
        
        if int(estado) == 1:
            queryCronograma.activo = False
            queryCronograma.save()
            return Response({'message': 'Cronograma desactivado', 'success': 'ok', 'data':''})
        elif int(estado)     == 0:
            queryCronograma.activo = True
            queryCronograma.save()
            return Response({'message': 'Cronograma activado', 'success': 'ok', 'data':''})
        
        else:
            return Response({"message": "No se pudo actualizar el estado del cronograma", "success": "error", "data":''})

    except Exception as e:
        functions.toLog(e, 'cronogramacontrato.VerSoporte')
        return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
            'data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@login_required
@transaction.atomic
def actualizar_capitulo(request):

    sid = transaction.savepoint()
    try:
        #import pdb; pdb.set_trace()
        lista=request.POST['_content']
        respuesta= json.loads(lista)
        #print ("texto")

        #lista=respuesta['lista'].split(',')
		
        for item in respuesta['lista']:
            queryCapitulo = CcCapitulo.objects.get(id=item['id'])
            queryCapitulo.orden = item['orden']
            queryCapitulo.save()
            logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='cronogramacontrato.CcCapitulo',id_manipulado=item['id'])
            logs_model.save()

		#return HttpResponse(str('0'), content_type="text/plain")
        transaction.savepoint_commit(sid)
        return JsonResponse({'message':'El registro se ha actualizado correctamente','success':'ok',
				'data':''})
    except ProtectedError:
        transaction.savepoint_rollback(sid)
        return JsonResponse({'message':'No es posible actualizado el registro, se esta utilizando en otra seccion del sistema','success':'error',
			'data':''})	
    except Exception as e:
        transaction.savepoint_rollback(sid)
        functions.toLog(e,'cronogramacontrato.actualizar_capitulo')
        return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	


@login_required
@transaction.atomic
def actualizar_actividad(request):

    sid = transaction.savepoint()
    try:
        ##import pdb; pdb.set_trace()
        lista=request.POST['_content']
        respuesta= json.loads(lista)
        #print ("texto")

        #lista=respuesta['lista'].split(',')
		
        for item in respuesta['lista']:
            queryActividad = CcActividad.objects.get(id=item['id'])
            queryActividad.orden = item['orden']
            queryActividad.descripcion = item['descripcion']
            queryActividad.inicioprogramado = item['inicioprogramado']
            queryActividad.finprogramado = item['finprogramado']
            queryActividad.requiereSoporte = item['requiereSoporte']
            queryActividad.soporteObservaciones = item['soporteObservaciones']
            queryActividad.save()
            logs_model=Logs(usuario_id=request.user.usuario.id,accion=Acciones.accion_actualizar,nombre_modelo='cronogramacontrato.CcActividad',id_manipulado=item['id'])
            logs_model.save()

		#return HttpResponse(str('0'), content_type="text/plain")
        transaction.savepoint_commit(sid)
        return JsonResponse({'message':'El registro se ha actualizado correctamente','success':'ok',
				'data':''})
    except ProtectedError:
        transaction.savepoint_rollback(sid)
        return JsonResponse({'message':'No es posible actualizado el registro, se esta utilizando en otra seccion del sistema','success':'error',
			'data':''})	
    except Exception as e:
        transaction.savepoint_rollback(sid)
        functions.toLog(e,'cronogramacontrato.actualizar_actividad')
        return JsonResponse({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''})	




@api_view(['GET'])
def listUrlsById(request):
    try:
        idactividad = request.query_params.get('id', None)
        queryActividadSoporte = CcActividadContratoSoporte.objects.filter(actividadcontrato__id = idactividad)
        if queryActividadSoporte.count() > 0:
                serializer = ActividadContratoSoporteSerializer(queryActividadSoporte,many=True, 
                        context={'request': request,})
                return Response({"message": "", "success": "ok", "data": serializer.data, 'cantidad': queryActividadSoporte.count()})
        else:
            return Response({'message' : "No se encontraron soportes para esa actividad", 
                "success": "ok", "data":[]})

    except Exception as e:
        functions.toLog(e, 'cronogramacontrato.VerSoporte')
        return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
            'data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def getListaContratos(request):
    #Contrato.objects.filter(tipo_contrato=12)
    try:
        
        #Empresa_contratoConsultaSerializer
        #EmpresaContrato
        # qset = Q(empresa__id=request.user.usuario.empresa.id,
         #contrato__tipo_contrato__id=12, contrato_id = id)

        qset = Q(empresa__id=request.user.usuario.empresa.id,
         contrato__tipo_contrato__id=12)

        querysetContratosConAcceso = EmpresaContrato.objects.filter(
            qset).values_list('contrato__id',flat=True)

        queryContratos = Contrato.objects.filter(
            id__in=list(querysetContratosConAcceso))


        if queryContratos.count() > 0:
            serializer = ContratoLiteSerializerByJs( queryContratos ,many=True, 
                        context={'request': request,})
            return Response({"message": "", "success": "ok", "data": serializer.data})       

    except Exception as e:
        functions.toLog(e, 'cronogramacontrato.getListaContratos')
        return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
            'data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def asociarCronogramaContrato(request):
    try:
        #import pdb; pdb.set_trace()
        contrato_id =  request.data['contrato_id']
        cronograma_id =  request.data['cronograma_id']
        queryContrato = Contrato.objects.get(id = contrato_id)
        queryActividades = CcActividad.objects.filter(capitulo__cronograma__id = cronograma_id)

        if queryActividades.count() > 0:
            
            queryAsociado = CcActividadContrato.objects.filter(contrato = queryContrato)
            if queryAsociado.count() > 0:
                return Response({"message": "No se pudo asociar el contrato pues ya existe una asociación previa a un cronograma",
                "success": "error", "data": ''})
         


            for i in range(queryActividades.count()):
                queryAsociar = CcActividadContrato(
                actividad_id = queryActividades[i].id,
                contrato = queryContrato,
                )
                queryAsociar.save()           
            
            return Response({"message": "Cronograma asociado correctamente",
             "success": "ok", "data": ''})        

        else:
            return Response({"message": "No se encontraron datos para esa actividad",
             "success": "ok", "data": ''})

    except Exception as e:
        functions.toLog(e, 'cronogramacontrato.asociarCronogramaContratos')
        return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
            'data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def getActivities(request):
    try:
        contrato_id = request.query_params.get('contrato_id', None)
        cronogramacontrato_id = request.query_params.get('cronogramacontrato_id', None)
        if contrato_id and cronogramacontrato_id:
            capitulos = CcCapitulo.objects.filter(
                cronograma__id=cronogramacontrato_id).values(
                'id','nombre').order_by('orden')

            if capitulos:    
                data = []
                  
                for capitulo in capitulos:
                    queryActividades = CcActividadContrato.objects.filter(
                        contrato__id = contrato_id,
                        actividad__capitulo__id = capitulo['id'],
                        ).order_by('actividad__orden')

                    arrayActividades = []
                    if queryActividades:

                        actividades = queryActividades.values(
                                'id',
                                'actividad__descripcion',
                                'inicioprogramado',
                                'finprogramado',
                                'inicioejecutado',
                                'finejecutado',
                                'estadoinicio__nombre',
                                'estadofin__nombre',
                                'observaciones',
                                'estadofin__codigo',
                                'actividad__inicioprogramado',
                                'actividad__finprogramado',
                                'actividad__requiereSoporte',
                                'actividad__soporteObservaciones'
                            )
                        actividadesTerminadas = 0
                        totalActividades = queryActividades.count()
                              
                        for actividad in actividades:
                            cantidadSoportes = CcActividadContratoSoporte.objects.filter(
                                actividadcontrato__id = actividad['id']
                                )
                            arrayActividades.append(
                                {
                                    'id' : actividad['id'],
                                    'descripcion' : actividad['actividad__descripcion'],
                                    'inicioprogramado' : actividad['inicioprogramado'],
                                    'finprogramado' : actividad['finprogramado'],
                                    'inicioejecutado' : actividad['inicioejecutado'],
                                    'finejecutado' : actividad['finejecutado'],
                                    'estadoinicio' : actividad['estadoinicio__nombre'],
                                    'estadofin' : actividad['estadofin__nombre'],
                                    'observaciones' : actividad['observaciones'],
                                    'cantidadSoportes' : cantidadSoportes.count(),
                                    'admiteinicioprogramado' : actividad['actividad__inicioprogramado'],
                                    'admitefinprogramado' : actividad['actividad__finprogramado'],
                                    'requieresoporte' : actividad['actividad__requiereSoporte'],
                                    'admiteobservaciones' : actividad['actividad__soporteObservaciones']
                                }
                            )
                            if actividad['estadofin__codigo'] == 172 or actividad['estadofin__codigo'] == 173:
                                actividadesTerminadas = actividadesTerminadas + 1

                        data.append(
                            {
                                'id' : capitulo['id'],
                                'nombre' : capitulo['nombre'],
                                'avance' : round((float(actividadesTerminadas) / float(totalActividades))*100,2),
                                'actividades' : arrayActividades
                            }
                        )

                return Response({"message": "", "success": "ok", "data": data})
            else:
                return Response({
                    'message' : "No se encontraron capitulos asociados al contrato", 
                    "success": "error", "data":''})                    
                        

        else:
            return Response({'message' : "No se recibió el contrato y el esquema del cronograma", 
                "success": "error", "data":''})


    except Exception as e:
        functions.toLog(e, 'cronogramacontrato.getActivites')
        return Response({'message':'Se presentaron errores al procesar los datos','success':'error',
            'data':''},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def editarProgramacion(request):
    try:
        #import pdb; pdb.set_trace()
        actividadcontrato_id = request.DATA['actividadcontrato_id']
        inicioprogramado = request.DATA['inicioprogramado']
        finprogramado = request.DATA['finprogramado']

        if actividadcontrato_id and inicioprogramado and finprogramado:
            actividadContrato = CcActividadContrato.objects.get(id=actividadcontrato_id)
            if actividadContrato:
                actividadContrato.inicioprogramado = inicioprogramado
                hoy = datetime.now()
                inicio = datetime.strptime(inicioprogramado, '%Y-%m-%d')
                estadoInicio = None
                if inicio < hoy:
                    estadoInicio = Estado.objects.filter(
                        codigo=168,app='cronogramacontrato_estadoinicio').first()
                else:
                    limite = inicio - timedelta(days=7)
                    if hoy < limite:
                        #A tiempo
                        estadoInicio = Estado.objects.filter(
                            codigo=165,app='cronogramacontrato_estadoinicio').first()
                    else:
                        #Proximo a iniciar
                        estadoInicio = Estado.objects.filter(
                            codigo=166,app='cronogramacontrato_estadoinicio').first()
                if estadoInicio:
                    actividadContrato.estadoinicio = estadoInicio

                fin = datetime.strptime(finprogramado, '%Y-%m-%d')
                estadoFin = None
                if fin < hoy:
                    estadoFin = Estado.objects.filter(
                        codigo=171,app='cronogramacontrato_estadofin').first()
                else:
                    porvencer = fin - timedelta(days=7)
                    if hoy > porvencer:
                        #Por vencer
                        estadoFin = Estado.objects.filter(
                            codigo=170,app='cronogramacontrato_estadofin').first()
                    else:
                        #Por cumplir
                        estadoFin = Estado.objects.filter(
                            codigo=174,app='cronogramacontrato_estadofin').first()

                if estadoFin:
                    actividadContrato.estadofin = estadoFin

                actividadContrato.finprogramado = finprogramado
                actividadContrato.save()
                return Response({"message": "La actividad ha sido programada correctamente",
                 "success": "ok", "data": []},status=status.HTTP_200_OK)

            else:
                return Response({'message' : "No se encontró el registro para programarlo", 
                    "success": "error", "data":''},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({'message' : "No se recibieron todos los parametros", 
                "success": "error", "data":''},status=status.HTTP_406_NOT_ACCEPTABLE)

    except Exception as e:
        functions.toLog(e, 'cronogramacontrato.editarProgramacion')
        return Response({'message':'Se presentaron errores al procesar los datos',
            'success':'error',
            'data':''
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def registarInicioActividad(request):
    try:
        actividadcontrato_id = request.DATA['actividadcontrato_id']
        fecha = request.DATA['fecha']
        observaciones = request.DATA['observaciones']
    
        if actividadcontrato_id and fecha and observaciones:
            actividadContrato = CcActividadContrato.objects.get(id=actividadcontrato_id)
    
            if actividadContrato:
                estadoInicio = None
                actividadContrato.inicioejecutado = fecha
    
                dateRegistroInicio = datetime.strptime(fecha, '%Y-%m-%d').date()
                if actividadContrato.inicioprogramado:

                    if actividadContrato.inicioprogramado >= dateRegistroInicio:
                        estadoinicio = Estado.objects.filter(
                            codigo=167,app='cronogramacontrato_estadoinicio').first()  
                    else:
                        estadoinicio = Estado.objects.filter(
                            codigo=169,app='cronogramacontrato_estadoinicio').first()                      
    
                else:
                    estadoinicio = Estado.objects.filter(
                        codigo=167,app='cronogramacontrato_estadoinicio').first()
    
                actividadContrato.estadoinicio = estadoinicio
                actividadContrato.observaciones = observaciones
    
                actividadContrato.save()
                return Response({"message": "La actividad ha sido iniciada correctamente",
                 "success": "ok", "data": []},status=status.HTTP_200_OK)
            else:
                return Response({'message' : "No se encontró la actividad para iniciarla", 
                    "success": "error", "data":''},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({'message' : "No se recibieron todos los parametros", 
                "success": "error", "data":''},status=status.HTTP_406_NOT_ACCEPTABLE)              

    except Exception as e:
        functions.toLog(e, 'cronogramacontrato.registroInicioActividad')
        return Response({'message':'Se presentaron errores al procesar los datos',
            'success':'error',
            'data':''
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def registarFinActividad(request):
    try:
        actividadcontrato_id = request.DATA['actividadcontrato_id']
        fecha = request.DATA['fecha']
        observaciones = request.DATA['observaciones']
    
        if actividadcontrato_id and fecha and observaciones:
            actividadContrato = CcActividadContrato.objects.get(id=actividadcontrato_id)
    
            if actividadContrato:
                estadoFin = None
                actividadContrato.finejecutado = fecha
    
                dateRegistroFin = datetime.strptime(fecha, '%Y-%m-%d').date()

                if actividadContrato.finprogramado:
                    if actividadContrato.finprogramado >= dateRegistroFin:
                        estadoFin = Estado.objects.filter(
                            codigo=172,app='cronogramacontrato_estadofin').first()  
                    else:
                        estadoFin = Estado.objects.filter(
                            codigo=173,app='cronogramacontrato_estadofin').first()

                else:
                    estadoFin = Estado.objects.filter(codigo=172,
                        app='cronogramacontrato_estadofin').first()

                actividadContrato.estadofin = estadoFin
                actividadContrato.observaciones = observaciones
    
                actividadContrato.save()
                return Response({"message": "La actividad ha sido finalizada correctamente",
                 "success": "ok", "data": []},status=status.HTTP_200_OK)

            else:
                return Response({'message' : "No se encontró la actividad para iniciarla", 
                    "success": "error", "data":''},status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({'message' : "No se recibieron todos los parametros", 
                "success": "error", "data":''},status=status.HTTP_406_NOT_ACCEPTABLE)              
    except Exception as e:
        functions.toLog(e, 'cronogramacontrato.registroFinActividad')
        return Response({'message':'Se presentaron errores al procesar los datos',
            'success':'error',
            'data':''
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
