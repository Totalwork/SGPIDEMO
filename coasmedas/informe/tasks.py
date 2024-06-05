# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from sinin4.celery import app
from adminMail.models import Mensaje
from django.db import transaction, connection
from django.http import HttpResponse,JsonResponse
# from usuario.models import Usuario
import uuid
from django.conf import settings
import os
import xlsxwriter
from sinin4.functions import functions
import json
import re
import boto 
from boto.s3.key import Key
from datetime import *
try:
	from StringIO from io import StringIO
except ImportError:
	from io import StringIO
import io	

def crearMapaInforme(nombre, ruta):	
	cursor = connection.cursor()
	try:
		output = io.BytesIO()		
		workbook = xlsxwriter.Workbook(output, {'in_memory': True})
		worksheet = workbook.add_worksheet('listado')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
		format_money = workbook.add_format({'border':1, 'num_format': '$#,##0'})

		cursor.callproc('[dbo].[mapa_archivos_sinin]', [nombre])		
		columns = cursor.description 
		length_list = [len(x) for x in columns]
		lista = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		for i, width in enumerate(length_list):
			worksheet.set_column(i, i, 30)

		columnasV = []
		i = 0
		for col in columns:
			columnasV.append({'columna':columns[i][0], 'tipo': columns[i][3]})
			i = i + 1

		col = 0	
		for column in columnasV:							
			worksheet.write(0, col, column['columna'], format1)
			col = col + 1

		row=1				
		for item in lista:
			col=0				
			for column in columnasV:				
				worksheet.write(row, col, item[column['columna']], format2)
				col = col + 1
			row = row + 1	
			
		workbook.close()
	

		try:
			ayer = datetime.today() - timedelta(days=1)
			archivo=str(ayer.year)+str(ayer.month)+str(ayer.day)
			functions.eliminarArchivoS3('{0}/0000-guia{1}.xlsx'.format(ruta, archivo))
		except Exception as e:
			pass

		ahora=datetime.now()		
		archivo=str(ahora.year)+str(ahora.month)+str(ahora.day)
		return functions.subirArchivoS3('{0}/0000-guia{1}.xlsx'.format(ruta, archivo), output)
		
	except Exception as e:
		functions.toLog(e, 'informe.crearMapaInforme')
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''})

@app.task
def generarMapaArchivos():	
	try:
		crearMapaInforme('administrador fotos', 'administrador_fotos/fotos_proyecto')
		crearMapaInforme('administrador fotos subcategoria fotos', 'administrador_fotos/subcategoria_fotos')
		crearMapaInforme('contratos', 'contrato')
		crearMapaInforme('correspondencia enviada', 'correspondencia')
		crearMapaInforme('correspondencia recibida', 'correspondencia_recibida')
		crearMapaInforme('facturas', 'factura/factura')
		crearMapaInforme('factura descuento', 'factura/descuento')
		crearMapaInforme('factura cesion', 'factura/cesion')
		crearMapaInforme('gestion proyecto', 'gestion_proyecto')
		crearMapaInforme('financiero', 'financiero')
		crearMapaInforme('giros detalle giro', 'giros/encabezado_giro')
		crearMapaInforme('giros consecutivo deshabilitado', 'giros/consecutivo_desahabilitado')	
		crearMapaInforme('mi nube', 'mi_nube')
		crearMapaInforme('multa apelacion', 'multa-apelacion')
		crearMapaInforme('multa historial', 'multa-historial')
		crearMapaInforme('multa solicitud', 'multa-solicitud')
		crearMapaInforme('no conformidad', 'no_conformidad')
		crearMapaInforme('polizas', 'poliza/soporte')
		crearMapaInforme('procesos', 'procesos/soportes')
		crearMapaInforme('retie', 'retie/soporte')
		crearMapaInforme('seguridad social empleados', 'seguridad_social')
		crearMapaInforme('seguridad social planilla', 'seguridad_social/planillas')			
		crearMapaInforme('administrador tarea', 'tarea')
		return JsonResponse({'message':'Las guias fueron creadas satisfactoriamente.','success':'ok','data': None})
	except Exception as e:
		functions.toLog(e, 'informe.generarMapaArchivos')
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''})


def crearInformeDinamico(opcion):	
	cursor = connection.cursor()
	try:
		
		output = io.BytesIO()
		workbook = xlsxwriter.Workbook(output, {'in_memory': True})
		worksheet = workbook.add_worksheet('listado')
		format1=workbook.add_format({'border':1,'font_size':12,'bold':True, 'bg_color':'#4a89dc','font_color':'white'})
		format2=workbook.add_format({'border':1})
		format_date=workbook.add_format({'border':1,'num_format': 'yyyy-mm-dd'})
		format_money = workbook.add_format({'border':1, 'num_format': '$#,##0'})

		cursor.callproc('[dbo].[consultar_informe_dinamico]', [opcion, 4, ''])		
		columns = cursor.description 
		length_list = [len(x) for x in columns]
		lista = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
		for i, width in enumerate(length_list):
			worksheet.set_column(i, i, 30)
		
		columnasV = []
		i = 0
		for col in columns:
			columnasV.append({'columna':columns[i][0], 'tipo': columns[i][3]})
			i = i + 1

		col = 0	
		for column in columnasV:						
			worksheet.write(0, col, column['columna'], format1)
			col = col + 1

		row=1				
		for item in lista:
			col=0				
			for column in columnasV:				
				if column['tipo'] == 10:
					worksheet.write(row, col, item[column['columna']], format_date)
				elif column['columna'] == 'Valor':
					worksheet.write(row, col, item[column['columna']], format_money)	
				elif column['columna'] == 'Soporte':
					worksheet.write_url(row, col, item[column['columna']], string='Ver Soporte', cell_format=format2)		
				else:	
					worksheet.write(row, col, item[column['columna']], format2)
				col = col + 1
			row = row + 1	
			
		workbook.close()	
		return functions.subirArchivoS3('datos_sinin_eca/{0}.xlsx'.format(opcion), output)
	except Exception as e:
		functions.toLog(e, 'informe.tasks.generarInformeDinamico')
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''})

@app.task
def generarInformeDinamico():
	try:
		print (crearInformeDinamico("contratos"))
		print (crearInformeDinamico("vigencias-contrato"))
		print (crearInformeDinamico("proyectos"))
		print (crearInformeDinamico("facturas"))
		print (crearInformeDinamico("detalle giros"))
		print (crearInformeDinamico("correspondencias enviadas"))
		print (crearInformeDinamico("correspondencias recibidas"))
		print (crearInformeDinamico("empleados"))
		print (crearInformeDinamico("planillas"))
		print (crearInformeDinamico("cuentas"))
		print (crearInformeDinamico("extracto de cuentas"))
		print (crearInformeDinamico("contratistas"))
		print (crearInformeDinamico("gestion de proyectos"))
		print (crearInformeDinamico("multas"))
		print (crearInformeDinamico("polizas"))
		return JsonResponse({'message':'Los informes fueron creados satisfactoriamente.','success':'ok','data': None})
	except Exception as e:
		functions.toLog(e, 'informe.tasks.generarInformeDinamico')
		return JsonResponse({'message':'Se presentaron errores de comunicacion con el servidor','status':'error','data':''})