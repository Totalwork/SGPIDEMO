# -*- coding: utf-8 -*-
from coasmedas.celery import app
from adminMail.models import Mensaje
from django.db.models import Q, query
from django.conf import settings
from coasmedas.functions import functions
from .models import CcActividadContrato
from parametrizacion.models import Notificacion
from usuario.models import Persona
from datetime import datetime, timedelta
from estado.models import Estado
import xlsxwriter
import os

@app.task
def actualizarEstadoInicio():
	try:
		actividadContratos = CcActividadContrato.objects.filter(
			inicioejecutado__isnull=True,
			inicioprogramado__isnull=False).values('inicioprogramado','id')
		hoy = datetime.now().date()

		for actividadContrato in actividadContratos:
			estadoInicio = None

			inicioProgramado = actividadContrato['inicioprogramado']
			if inicioProgramado < hoy:
				#Retrasado
				estadoInicio = Estado.objects.filter(
					codigo=168,app='cronogramacontrato_estadoinicio').first()
			else:
				limite = inicioProgramado - timedelta(days=7)
				if hoy < limite:
					#A tiempo
					estadoInicio = Estado.objects.filter(
						codigo=165,app='cronogramacontrato_estadoinicio').first()
				else:
					#Proximo a iniciar
					estadoInicio = Estado.objects.filter(
						codigo=166,app='cronogramacontrato_estadoinicio').first()


			objActividadContrato = CcActividadContrato.objects.get(
				id = actividadContrato['id'])


			if objActividadContrato:
				objActividadContrato.estadoinicio = estadoInicio
				objActividadContrato.save()


	except Exception as e:
		functions.toLog(e,'cronogramacontrato.tasks.actualizarEstadoInicio')

@app.task
def actualizarEstadoFin():
	try:
		actividadContratos = CcActividadContrato.objects.filter(
			finejecutado__isnull=True,
			finprogramado__isnull=False).values('finprogramado','id')
		hoy = datetime.now().date()

		for actividadContrato in actividadContratos:
			estadoFin = None

			finProgramado = actividadContrato['finprogramado']
			if finProgramado < hoy:
				#Vencida
				estadoFin = Estado.objects.filter(
					codigo=171,app='cronogramacontrato_estadofin').first()
			else:
				limite = finProgramado - timedelta(days=7)
				if hoy < limite:
					#Por cumplir
					estadoFin = Estado.objects.filter(
						codigo=174,app='cronogramacontrato_estadofin').first()
				else:
					#Por vencer
					estadoFin = Estado.objects.filter(
						codigo=170,app='cronogramacontrato_estadofin').first()


			objActividadContrato = CcActividadContrato.objects.get(
				id = actividadContrato['id'])


			if objActividadContrato:
				objActividadContrato.estadofin = estadoFin
				objActividadContrato.save()


	except Exception as e:
		functions.toLog(e,'cronogramacontrato.tasks.actualizarEstadoFin')


@app.task
def notificacionCambioDeEstados():
	try:
		print("Linea 97, contenido")
		contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
		contenido = contenido + "Estimado usuario(a),<br />Nos permitimos notificarle que las actividades relacionadas en el adjunto, se encuentran retrasadas o proximas a iniciar. En el adjunto podra diferenciar el estado de las actividades a traves de las columnas <b>estado inicio</b> y <b>estado fin</b><br /> ."
		contenido = contenido + '<br /><br /><br />Favor no responder este correo, es de uso informativo unicamente.<br /><br /><br />Gracias,<br /><br /><br />'
		contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'	
		unique_filename = 'Cronogramacontrato - '+str(datetime.today().date())
		ruta = settings.STATICFILES_DIRS[0]
		nombre_archivo = ruta+'\papelera\{}.xlsx'.format(unique_filename) 
		workbook = xlsxwriter.Workbook(nombre_archivo)
		worksheet = workbook.add_worksheet('Todos')
		worksheet.set_column('A:I', 19)
		worksheet.set_column('B:B', 30)
		worksheet.set_column('C:C', 30)
		worksheet.set_column('D:E', 23)
		bold = workbook.add_format({'bold': True, 'align': 'center', 'text_wrap': True})
		normal = workbook.add_format({'align': 'center', 'text_wrap': True})
		fecha = workbook.add_format({'align': 'center', 'num_format': 'yyyy/mm/dd'})

		worksheet.write('A1', 'Nombre de Contrato', bold, )
		worksheet.write('B1', 'Capitulo', bold)
		worksheet.write('C1', 'Actividad', bold)
		worksheet.write('D1', 'Fecha inicio programada', bold)
		worksheet.write('E1', 'Fecha inicio ejecutada', bold)
		worksheet.write('F1', 'Fecha fin programada', bold)
		worksheet.write('G1', 'Fecha fin ejecutada', bold)
		worksheet.write('H1', 'Estado inicio', bold)
		worksheet.write('I1', 'Estado fin', bold)

		valores = (Q(estadoinicio__codigo =168) | Q(estadoinicio__codigo =166) | Q(estadofin__codigo =171) | Q(estadofin__codigo =170) )
		queryActividadContrato = CcActividadContrato.objects.filter(valores).values(
			'contrato__nombre', 'actividad__capitulo__nombre', 
			'actividad__descripcion', 'inicioprogramado', 'inicioejecutado',
			'finprogramado', 'finejecutado', 'estadoinicio__nombre', 'estadofin__nombre'
			)
		# queryActividadContrato[1]['estadoinicio__nombre']
		
		
		listaCorreos = []

		
		# actividades = []
		if queryActividadContrato.count() > 0:
			pos = 2
			for valor in queryActividadContrato:
				nombre_contrato = valor['contrato__nombre']
				actividad_capitulo_nombre = valor['actividad__capitulo__nombre']
				actividad__descripcion = valor['actividad__descripcion']
				if valor['inicioprogramado'] == '':
					inicioprogramado = 'Pendiente'
				else:
					inicioprogramado = valor['inicioprogramado']
				
				if valor['inicioejecutado'] == '':
					inicioejecutado = 'Pendiente'
				else:
					inicioejecutado = valor['inicioejecutado']

				if valor['finprogramado'] == '':
					finprogramado = 'Pendiente'
				else:
					finprogramado = valor['finprogramado']
					
				
				if valor['finejecutado'] == '':
					finejecutado = 'Pendiente'
				else:
					finejecutado = valor['finejecutado']


				if valor['estadoinicio__nombre'] == '':
					estadoinicio__nombre = 'Pendiente'

				else:
					estadoinicio__nombre = valor['estadoinicio__nombre']
				
				if valor['estadofin__nombre'] == '':
					estadofin__nombre = 'Pendiente'	
				else:
					estadofin__nombre = valor['estadofin__nombre']

				worksheet.write('A'+str(pos), nombre_contrato, normal, )
				worksheet.write('B'+str(pos), actividad_capitulo_nombre, normal)
				worksheet.write('C'+str(pos), actividad__descripcion, normal)
				worksheet.write('D'+str(pos), inicioprogramado, fecha)
				worksheet.write('E'+str(pos), inicioejecutado, fecha)
				worksheet.write('F'+str(pos), finprogramado, fecha)
				worksheet.write('G'+str(pos), finejecutado, fecha)
				worksheet.write('H'+str(pos), estadoinicio__nombre, normal)
				worksheet.write('I'+str(pos), estadofin__nombre, normal)
				pos += 1
			
			workbook.close()
			destinatarios = ''
			queryNotificacion = Notificacion.objects.get(nombre='notificacionCambioDeEstados')
			queryPersona = queryNotificacion.usuario_cc.all()
			if len(queryPersona) > 0:
				for p in queryPersona:
					listaCorreos.append(p.correo)
			
			if len(listaCorreos) > 0:
				
				for c in listaCorreos:
					destinatarios += c + '; '
			



			mail = Mensaje(
						remitente=settings.REMITENTE,
						destinatario=destinatarios,
						asunto='Informe de actividades que están retrasadas o proximas a iniciar',
						contenido=contenido,
						appLabel='cronogramacontrato',
						tieneAdjunto=True,
						adjunto=nombre_archivo,
						copia=''
						)
			mail.Send()
			if os.path.exists(nombre_archivo):
				os.remove(nombre_archivo)

	except Exception as e:
		functions.toLog(e,'notificacionCambioDeEstados')


		
