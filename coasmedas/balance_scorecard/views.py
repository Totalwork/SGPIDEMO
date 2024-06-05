from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required


from django.db import transaction,connection
from django.db.models.deletion import ProtectedError
from django.template import RequestContext
from django.http import HttpResponse,JsonResponse

from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from proyecto.models import Proyecto
from contrato.models import Contrato, EmpresaContrato
from contrato.enumeration import tipoC
# from datetime import *
from logs.models import Logs,Acciones


@login_required
def balance_scorecard(request):
	return render(request, 'balance_scorecard/inicio.html',{'model':'balance_scorecard','app':'balance_scorecard'})

@login_required
def aspectos_financieros(request):
	return render(request, 'balance_scorecard/aspectos_finacieros.html',{'model':'balance_scorecard','app':'balance_scorecard'})

@login_required
def procesos_internos(request):
	return render(request, 'balance_scorecard/procesos_internos.html',{'model':'balance_scorecard','app':'balance_scorecard'})

@login_required
def cultura_organizacional(request):
	return render(request, 'balance_scorecard/cultura_organizacional.html',{'model':'balance_scorecard','app':'balance_scorecard'})

@login_required
def consultarpordepartamento(request):
	# if request.method == 'GET':
	cursor = connection.cursor()
	
	try:
		tipo_tarjeta= request.GET['tipo_tarjeta'] if 'tipo_tarjeta' in request.GET else 0;


		qset = (Q(contrato__tipo_contrato=tipoC.m_contrato))& (Q(edita='1')) &(Q(empresa=4) & Q(participa=1))
		ListMacro = EmpresaContrato.objects.filter(qset).values('contrato_id').order_by("contrato_id")
		
		if int(tipo_tarjeta)==3:
			aux=Proyecto.objects.select_related('proyecto_contrato').filter(tipo_proyecto__fondo_proyecto__id=2,mcontrato__id__in=ListMacro).values('municipio__departamento_id','municipio__departamento__nombre').distinct().order_by('municipio__departamento__nombre')
		elif int(tipo_tarjeta)==4:
			aux=Proyecto.objects.select_related('proyecto_contrato').filter(tipo_proyecto__fondo_proyecto__id=1,mcontrato__id__in=ListMacro).values('municipio__departamento_id','municipio__departamento__nombre').distinct().order_by('municipio__departamento__nombre')
		else:
			aux=Proyecto.objects.select_related('proyecto_contrato').filter(mcontrato__id__in=ListMacro).values('municipio__departamento_id','municipio__departamento__nombre').distinct().order_by('municipio__departamento__nombre')
		
		Listdepartamento=[]
		for p in list(aux):
			Listdepartamento.append({
				'id': p['municipio__departamento_id'], 
				'nombre': p['municipio__departamento__nombre']})
		

		if int(tipo_tarjeta)==1 or int(tipo_tarjeta)==2:

			Lista_departamentos=[]			
			for dep in Listdepartamento:
				
				aux_mcontrato = Proyecto.objects.select_related('proyecto_contrato').filter(municipio__departamento_id=int(dep['id']),mcontrato__id__in=ListMacro).values('mcontrato__id').distinct().order_by('mcontrato__id')
				
				porcentaje = 0
				count = 0
				for m in list(aux_mcontrato):
					cursor.callproc('[dbo].[bsc_aspectos_financieros_contratos]',[int(tipo_tarjeta),int(dep['id']),1,int(m['mcontrato__id'])])
					porcentaje_set = cursor.return_value
					porcentaje = porcentaje + porcentaje_set
					count = count + 1
				porcentaje = float(porcentaje / count)

				Lista_departamentos.append({
					'id': dep['id'], 
					'nombre': dep['nombre'], 
					'porcentaje':porcentaje})
	

		elif int(tipo_tarjeta)==3 or int(tipo_tarjeta)==4:
			Lista_departamentos=[]		

			valor = 0

			for dep in Listdepartamento:

				if int(tipo_tarjeta)==3:
					aux_mcontrato = Proyecto.objects.select_related('proyecto_contrato').filter(tipo_proyecto__fondo_proyecto__id=2,municipio__departamento_id=int(dep['id']),mcontrato__id__in=ListMacro).values('mcontrato__id').distinct().order_by('mcontrato__id')
				
				elif int(tipo_tarjeta)==4:
					aux_mcontrato = Proyecto.objects.select_related('proyecto_contrato').filter(tipo_proyecto__fondo_proyecto__id=1,municipio__departamento_id=int(dep['id']),mcontrato__id__in=ListMacro).values('mcontrato__id').distinct().order_by('mcontrato__id')
				
				valor_departamento = 0
				

				for m in list(aux_mcontrato):
					lista_temporal_contratos = []		
					
											
					cursor.callproc('[dbo].[bsc_aspectos_financieros_contratos]',[int(tipo_tarjeta),int(dep['id']),2,int(m['mcontrato__id'])])				
					valor_set = cursor.fetchall()
					valor_set = float(valor_set[0][0])

					valor_departamento = valor_departamento + valor_set

				valor = valor + valor_departamento

				
				Lista_departamentos.append({
					'id': dep['id'], 
					'nombre': dep['nombre'], 
					'porcentaje':0,
					'valor_total':valor_departamento})

			for d in Lista_departamentos:
				porcentaje = round(float (d['valor_total']*100/valor))
				d['porcentaje']=porcentaje
		

		# listado_principal.append({'departamentos':[{'id': p['municipio__departamento_id'], 'nombre': p['municipio__departamento__nombre'], 'porcentaje':30, 'valor':int(porcentaje)} for p in list(Listdepartamento)]})
		return JsonResponse({'message':'','success':'ok','data':Lista_departamentos})

	except Exception as e:
		print(e)
		return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)

	finally:
		cursor.close()

def contratopordepartamento(request):		
	cursor = connection.cursor()
	try:		

		id_departamento= request.GET['id_departamento'] if 'id_departamento' in request.GET else None;		
		tipo_tarjeta= request.GET['tipo_tarjeta'] if 'tipo_tarjeta' in request.GET else 0;
		
		qset = (Q(contrato__tipo_contrato=tipoC.m_contrato))& (Q(edita='1')) &(Q(empresa=4) & Q(participa=1))
		ListMacro = EmpresaContrato.objects.filter(qset).values('contrato_id').order_by("contrato_id")

		if int(tipo_tarjeta)==3:
			aux=Proyecto.objects.select_related('proyecto_contrato').filter(tipo_proyecto__fondo_proyecto__id=2,municipio__departamento = id_departamento,mcontrato__id__in=ListMacro).values('mcontrato__id','mcontrato__nombre').distinct().order_by('mcontrato__nombre')
		elif int(tipo_tarjeta)==4:
			aux=Proyecto.objects.select_related('proyecto_contrato').filter(tipo_proyecto__fondo_proyecto__id=1,municipio__departamento = id_departamento,mcontrato__id__in=ListMacro).values('mcontrato__id','mcontrato__nombre').distinct().order_by('mcontrato__nombre')
		else:
			aux = Proyecto.objects.select_related('proyecto_contrato').filter(municipio__departamento = id_departamento,mcontrato__id__in=ListMacro).values('mcontrato__nombre','mcontrato__id').distinct().order_by('mcontrato__nombre')	
		
		Listcontratos=[]
		for p in list(aux):
			Listcontratos.append({
				'id': p['mcontrato__id'], 
				'nombre': p['mcontrato__nombre'],
				'departamento_id': id_departamento})

		#import pdb; pdb.set_trace()			
		if int(tipo_tarjeta)==1 or int(tipo_tarjeta)==2:
			Lista_contratos=[]			
			for dep in Listcontratos:
				#import pdb; pdb.set_trace()
				cursor.callproc('[dbo].[bsc_aspectos_financieros_contratos]',[int(tipo_tarjeta),int(dep['departamento_id']),1,int(dep['id'])])
				porcentaje_set = cursor.return_value
				Lista_contratos.append({
					'id': dep['id'], 
					'nombre': dep['nombre'], 
					'porcentaje':porcentaje_set})
				
		if int(tipo_tarjeta)==3 or int(tipo_tarjeta)==4:
			Lista_contratos=[]			
			for dep in Listcontratos:
				#import pdb; pdb.set_trace()
				cursor.callproc('[dbo].[bsc_aspectos_financieros_contratos]',[int(tipo_tarjeta),int(dep['departamento_id']),1,int(dep['id'])])
				porcentaje_set = cursor.return_value				
				
				valor_set = None						
				cursor.callproc('[dbo].[bsc_aspectos_financieros_contratos]',[int(tipo_tarjeta),int(dep['departamento_id']),2,int(dep['id'])])				
				valor_set = cursor.fetchall()
				
				Lista_contratos.append({
					'id': dep['id'], 
					'nombre': dep['nombre'], 
					'porcentaje':porcentaje_set,
					'valor_total':float(valor_set[0][0])})


		
		
		return JsonResponse({'message':'','success':'ok','data':Lista_contratos})
	except Exception as e:
		print(e)
		return Response({'message':'Se presentaron errores al procesar la solicitud','success':'error',
			'data':''},status=status.HTTP_400_BAD_REQUEST)
	# finally:
	# 	cursor.close()				
# Create your views here.
