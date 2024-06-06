# -*- coding: utf-8 -*-
from coasmedas.celery import app

from django.db import connection
from django.db.models import Q
from django.http import HttpResponse
from django.conf import settings

from .models import Acta, Compromiso
from .enumeration import estadoA, estadoC

from parametrizacion.models import Notificacion, Funcionario
from adminMail.models import Mensaje
from coasmedas.functions import functions
from estado.models import Estado
import xlsxwriter
import uuid
import os

from datetime import *
import calendar



@app.task
def cambioEstadoActa():	
	today = date.today()
	date1 = today.strftime("%Y-%m-%d")	
	qset = (Q(fecha = date1))
	listActas = Acta.objects.filter(qset)
	if listActas:
		for l in listActas:
			acta = Acta.objects.get(pk=int(l.id))
			if acta:
				acta.estado_id = estadoA.en_curso
				acta.save()

@app.task
def cambioEstadoCompromiso():	
	today = date.today()
	date1 = today.strftime("%Y-%m-%d")	
	
	#por vencer
	qset = (Q(fecha_proximidad = date1))	
	listCompromisosPorVencer = Compromiso.objects.filter(qset)
	if listCompromisosPorVencer:
		for l in listCompromisosPorVencer:
			compromisoPorVencer = Compromiso.objects.get(pk=int(l.id))
			if compromisoPorVencer:
				compromisoPorVencer.estado_id = estadoC.por_vencer
				compromisoPorVencer.save()	

	#vencidos
	qset = (Q(fecha_compromiso__lt = date1))	
	listCompromisosVencidos = Compromiso.objects.filter(qset)
	if listCompromisosVencidos:
		for l in listCompromisosVencidos:
			compromisoVencidos = Compromiso.objects.get(pk=int(l.id))
			if compromisoVencidos:
				compromisoVencidos.estado_id = estadoC.vencido
				compromisoVencidos.save()	

@app.task
def notificacion_compromisos():
	try:
		today = date.today()
		date1 = today.strftime("%Y-%m-%d")
		estados = [estadoC.por_vencer,estadoC.vencido]
		for estado in estados:

			if estado==estadoC.por_vencer:
				supervisores = Compromiso.objects.filter(fecha_proximidad__lte=date1,estado__id=estado).values('supervisor__id','supervisor__persona__nombres','supervisor__persona__apellidos','supervisor__persona__correo').distinct()			
				responsables_internos = Compromiso.objects.filter(fecha_proximidad__lte=date1,estado__id=estado,responsable_interno=True).values('usuario_responsable__id','usuario_responsable__persona__nombres','usuario_responsable__persona__apellidos','usuario_responsable__persona__correo').distinct()
				responsables_externos = Compromiso.objects.filter(fecha_proximidad__lte=date1,estado__id=estado,responsable_interno=False).values('participante_responsable__id','participante_responsable__persona__nombres','participante_responsable__persona__apellidos','participante_responsable__persona__correo').distinct()			
				organizadores =  Compromiso.objects.filter(fecha_proximidad__lte=date1,estado__id=estado,notificar_organizador=True).values('acta__usuario_organizador__id','acta__usuario_organizador__persona__nombres','acta__usuario_organizador__persona__apellidos','acta__usuario_organizador__persona__correo').distinct()
				controladores =   Compromiso.objects.filter(fecha_proximidad__lte=date1,estado__id=estado,notificar_controlador=True).values('acta__controlador_actual__id','acta__controlador_actual__persona__nombres','acta__controlador_actual__persona__apellidos','acta__controlador_actual__persona__correo').distinct()
			
			elif estado==estadoC.vencido:
				supervisores = Compromiso.objects.filter(fecha_compromiso__lte=date1,estado__id=estado).values('supervisor__id','supervisor__persona__nombres','supervisor__persona__apellidos','supervisor__persona__correo').distinct()			
				responsables_internos = Compromiso.objects.filter(fecha_compromiso__lte=date1,estado__id=estado,responsable_interno=True).values('usuario_responsable__id','usuario_responsable__persona__nombres','usuario_responsable__persona__apellidos','usuario_responsable__persona__correo').distinct()
				responsables_externos = Compromiso.objects.filter(fecha_compromiso__lte=date1,estado__id=estado,responsable_interno=False).values('participante_responsable__id','participante_responsable__persona__nombres','participante_responsable__persona__apellidos','participante_responsable__persona__correo').distinct()			
				organizadores =  Compromiso.objects.filter(fecha_compromiso__lte=date1,estado__id=estado,notificar_organizador=True).values('acta__usuario_organizador__id','acta__usuario_organizador__persona__nombres','acta__usuario_organizador__persona__apellidos','acta__usuario_organizador__persona__correo').distinct()
			

			participantes_notificados = []			

			if supervisores:
				for p in list(supervisores):
					participantes_notificados.append({
						'id':p['supervisor__id'],
						'nombres': p['supervisor__persona__nombres'], 
						'apellidos': p['supervisor__persona__apellidos'], 
						'correo': p['supervisor__persona__correo'],
						'tipo':'interno',
						})
			
			if responsables_internos:
				for p in list(responsables_internos):
					participantes_notificados.append({
						'id':p['usuario_responsable__id'],
						'nombres': p['usuario_responsable__persona__nombres'], 
						'apellidos': p['usuario_responsable__persona__apellidos'], 
						'correo': p['usuario_responsable__persona__correo'],
						'tipo':'interno',
						})
			
			if responsables_externos:
				for p in list(responsables_externos):
					participantes_notificados.append({
						'id':p['participante_responsable__id'],
						'nombres': p['participante_responsable__persona__nombres'], 
						'apellidos': p['participante_responsable__persona__apellidos'], 
						'correo': p['participante_responsable__persona__correo'],
						'tipo':'externo',
						} )
				
			if organizadores:
				for p in list(organizadores):
					participantes_notificados.append({
						'id':p['acta__usuario_organizador__id'],
						'nombres': p['acta__usuario_organizador__persona__nombres'], 
						'apellidos': p['acta__usuario_organizador__persona__apellidos'], 
						'correo': p['acta__usuario_organizador__persona__correo'],
						'tipo':'interno',
						})
				
			if controladores:
				for p in list(controladores):
					participantes_notificados.append({
						'id':p['acta__controlador_actual__id'],
						'nombres': p['acta__controlador_actual__persona__nombres'], 
						'apellidos': p['acta__controlador_actual__persona__apellidos'], 
						'correo': p['acta__controlador_actual__persona__correo'],
						'tipo':'interno',
						})
				
			
			
			participantes_notificadosAgrupados=[]
			for item in participantes_notificados:
				agregar = True
				for obj in participantes_notificadosAgrupados:
					if item['nombres'] == obj['nombres'] and item['apellidos'] == obj['apellidos'] and item['correo'] == obj['correo']:							
						agregar = False
				if agregar:		
					participantes_notificadosAgrupados.append(item)	

			
			
			if participantes_notificadosAgrupados:				

				for participante in participantes_notificadosAgrupados:
					correo_envio = ''
					contenido = ''

					#print(participante['correo'])
					#import pdb; pdb.set_trace()	
					if participante['tipo']=='interno':	
						
						if estado==estadoC.por_vencer:
							comprosmisos_participante_interno = Compromiso.objects.filter(fecha_proximidad__lte=date1,estado__id=estado,responsable_interno=True,usuario_responsable__id=int(participante['id'])).values(
								'id',
								'acta__consecutivo',
								'acta__usuario_organizador__persona__nombres','acta__usuario_organizador__persona__apellidos',
								'acta__controlador_actual__persona__nombres','acta__controlador_actual__persona__apellidos',
								'supervisor__persona__nombres','supervisor__persona__apellidos',
								'descripcion',
								'fecha_compromiso',
								'requiere_soporte',
								'responsable_interno',
								'participante_responsable__persona__nombres','participante_responsable__persona__apellidos',
								'usuario_responsable__persona__nombres','usuario_responsable__persona__apellidos')
							comprosmisos_supervisor = Compromiso.objects.filter(fecha_proximidad__lte=date1,estado__id=estado,supervisor__id=int(participante['id'])).values(
								'id',
								'acta__consecutivo',
								'acta__usuario_organizador__persona__nombres','acta__usuario_organizador__persona__apellidos',
								'acta__controlador_actual__persona__nombres','acta__controlador_actual__persona__apellidos',
								'supervisor__persona__nombres','supervisor__persona__apellidos',
								'descripcion',
								'fecha_compromiso',
								'requiere_soporte',
								'responsable_interno',
								'participante_responsable__persona__nombres','participante_responsable__persona__apellidos',
								'usuario_responsable__persona__nombres','usuario_responsable__persona__apellidos')
							comprosmisos_organizador = Compromiso.objects.filter(fecha_proximidad__lte=date1,estado__id=estado,notificar_organizador=True,acta__usuario_organizador__id=int(participante['id'])).values(
								'id',
								'acta__consecutivo',
								'acta__usuario_organizador__persona__nombres','acta__usuario_organizador__persona__apellidos',
								'acta__controlador_actual__persona__nombres','acta__controlador_actual__persona__apellidos',
								'supervisor__persona__nombres','supervisor__persona__apellidos',
								'descripcion',
								'fecha_compromiso',
								'requiere_soporte',
								'responsable_interno',
								'participante_responsable__persona__nombres','participante_responsable__persona__apellidos',
								'usuario_responsable__persona__nombres','usuario_responsable__persona__apellidos')
							comprosmisos_controlador = Compromiso.objects.filter(fecha_proximidad__lte=date1,estado__id=estado,notificar_controlador=True,acta__controlador_actual__id=int(participante['id'])).values(
								'id',
								'acta__consecutivo',
								'acta__usuario_organizador__persona__nombres','acta__usuario_organizador__persona__apellidos',
								'acta__controlador_actual__persona__nombres','acta__controlador_actual__persona__apellidos',
								'supervisor__persona__nombres','supervisor__persona__apellidos',
								'descripcion',
								'fecha_compromiso',
								'requiere_soporte',
								'responsable_interno',
								'participante_responsable__persona__nombres','participante_responsable__persona__apellidos',
								'usuario_responsable__persona__nombres','usuario_responsable__persona__apellidos')
							
						elif estado==estadoC.vencido:
							comprosmisos_participante_interno = Compromiso.objects.filter(fecha_compromiso__lte=date1,estado__id=estado,responsable_interno=True,usuario_responsable__id=int(participante['id'])).values(
								'id',
								'acta__consecutivo',
								'acta__usuario_organizador__persona__nombres','acta__usuario_organizador__persona__apellidos',
								'acta__controlador_actual__persona__nombres','acta__controlador_actual__persona__apellidos',
								'supervisor__persona__nombres','supervisor__persona__apellidos',
								'descripcion',
								'fecha_compromiso',
								'requiere_soporte',
								'responsable_interno',
								'participante_responsable__persona__nombres','participante_responsable__persona__apellidos',
								'usuario_responsable__persona__nombres','usuario_responsable__persona__apellidos')
							comprosmisos_supervisor = Compromiso.objects.filter(fecha_compromiso__lte=date1,estado__id=estado,supervisor__id=int(participante['id'])).values(
								'id',
								'acta__consecutivo',
								'acta__usuario_organizador__persona__nombres','acta__usuario_organizador__persona__apellidos',
								'acta__controlador_actual__persona__nombres','acta__controlador_actual__persona__apellidos',
								'supervisor__persona__nombres','supervisor__persona__apellidos',
								'descripcion',
								'fecha_compromiso',
								'requiere_soporte',
								'responsable_interno',
								'participante_responsable__persona__nombres','participante_responsable__persona__apellidos',
								'usuario_responsable__persona__nombres','usuario_responsable__persona__apellidos')
							comprosmisos_organizador = Compromiso.objects.filter(fecha_compromiso__lte=date1,estado__id=estado,notificar_organizador=True,acta__usuario_organizador__id=int(participante['id'])).values(
								'id',
								'acta__consecutivo',
								'acta__usuario_organizador__persona__nombres','acta__usuario_organizador__persona__apellidos',
								'acta__controlador_actual__persona__nombres','acta__controlador_actual__persona__apellidos',
								'supervisor__persona__nombres','supervisor__persona__apellidos',
								'descripcion',
								'fecha_compromiso',
								'requiere_soporte',
								'responsable_interno',
								'participante_responsable__persona__nombres','participante_responsable__persona__apellidos',
								'usuario_responsable__persona__nombres','usuario_responsable__persona__apellidos')
							comprosmisos_controlador = Compromiso.objects.filter(fecha_compromiso__lte=date1,estado__id=estado,notificar_controlador=True,acta__controlador_actual__id=int(participante['id'])).values(
								'id',
								'acta__consecutivo',
								'acta__usuario_organizador__persona__nombres','acta__usuario_organizador__persona__apellidos',
								'acta__controlador_actual__persona__nombres','acta__controlador_actual__persona__apellidos',
								'supervisor__persona__nombres','supervisor__persona__apellidos',
								'descripcion',
								'fecha_compromiso',
								'requiere_soporte',
								'responsable_interno',
								'participante_responsable__persona__nombres','participante_responsable__persona__apellidos',
								'usuario_responsable__persona__nombres','usuario_responsable__persona__apellidos')
							
						compromisosAgrupados = []

						rol = '<br>'
						count_rol = 0

						#import pdb; pdb.set_trace()
						if comprosmisos_participante_interno:
							count_rol+=1
							rol = rol + '1. responsable '
							for item in comprosmisos_participante_interno:
								agregar = True
								for obj in compromisosAgrupados:
									if item['id'] == obj['id']:							
										agregar = False
								if agregar:		
									compromisosAgrupados.append(item)
						if comprosmisos_supervisor:							
							
							if count_rol>0:
								rol = rol +'<br>' + str(count_rol+1)+'. supervisor '
							elif count_rol==0:
								rol = rol + '1. supervisor '

							count_rol+=1
							for item in comprosmisos_supervisor:
								agregar = True
								for obj in compromisosAgrupados:
									if item['id'] == obj['id']:							
										agregar = False
								if agregar:		
									compromisosAgrupados.append(item)	
						if comprosmisos_organizador:
							if count_rol>0:
								rol = rol +'<br>'+ str(count_rol+1)+'. organizador '
							elif count_rol==0:
								rol = rol + '1. organizador '

							count_rol+=1
							for item in comprosmisos_organizador:
								agregar = True
								for obj in compromisosAgrupados:
									if item['id'] == obj['id']:							
										agregar = False
								if agregar:		
									compromisosAgrupados.append(item)	
						if comprosmisos_controlador:
							if count_rol>0:
								rol = rol +'<br>'+ str(count_rol+1)+'. controlador '
							elif count_rol==0:
								rol = rol + '1. controlador '

							count_rol+=1
							for item in comprosmisos_controlador:
								agregar = True
								for obj in compromisosAgrupados:
									if item['id'] == obj['id']:							
										agregar = False
								if agregar:		
									compromisosAgrupados.append(item)	


						
						if comprosmisos_participante_interno or comprosmisos_supervisor or comprosmisos_organizador or comprosmisos_controlador:

							correo_envio = correo_envio+participante['correo']+';'

							# INICIO - Crear el Excel
							# response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
							# response['Content-Disposition'] = 'attachment; filename="Reporte_contrato.xls"'

							# workbook = xlsxwriter.Workbook(response, {'in_memory': True})

							unique_filename = uuid.uuid4()
							nombre_archivo = '{}.xlsx'.format(unique_filename)
							workbook = xlsxwriter.Workbook(nombre_archivo)
							worksheet = workbook.add_worksheet('Contratos')

							worksheet.set_column('A:A', 10)
							worksheet.set_column('B:E', 30)
							worksheet.set_column('F:F', 35)
							worksheet.set_column('G:H', 20)

							format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
							format1.set_align('center')
							format1.set_align('vcenter')
							format2=workbook.add_format({'border':0})
							format5=workbook.add_format()
							format5.set_num_format('yyyy-mm-dd')

							row=1
							col=0

							worksheet.write('A1', 'No. acta', format1)
							worksheet.write('B1', 'Organizador', format1)
							worksheet.write('C1', 'Controlador', format1)
							worksheet.write('D1', 'Supervisor', format1)
							worksheet.write('E1', 'Responsable', format1)
							worksheet.write('F1', 'Descripción', format1)
							worksheet.write('G1', 'Fecha vencimiento', format1)
							worksheet.write('H1', 'Requiere soporte.', format1)

							

							for cont in compromisosAgrupados:
								worksheet.write(row, col,cont['acta__consecutivo'],format2)
								worksheet.write(row, col+1,cont['acta__usuario_organizador__persona__nombres']+' '+cont['acta__usuario_organizador__persona__apellidos'],format2)
								worksheet.write(row, col+2,cont['acta__controlador_actual__persona__nombres']+' '+cont['acta__controlador_actual__persona__apellidos'],format2)
								worksheet.write(row, col+3,cont['supervisor__persona__nombres']+' '+cont['supervisor__persona__apellidos'],format2)
								

								if cont['responsable_interno']:
									worksheet.write(row, col+4,cont['usuario_responsable__persona__nombres']+' '+cont['usuario_responsable__persona__apellidos'],format2)
								else:
									worksheet.write(row, col+4,cont['participante_responsable__persona__nombres']+' '+cont['participante_responsable__persona__apellidos'],format2)

								worksheet.write(row, col+5,cont['descripcion'],format2)
								worksheet.write(row, col+6,cont['fecha_compromiso'],format5)

								if cont['requiere_soporte']:
									worksheet.write(row, col+7,'Si',format2)
								else:
									worksheet.write(row, col+7,'No',format2)

								row +=1
							workbook.close()

							estado_nombre = Estado.objects.get(pk=estado)
							contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
							contenido+='Estimado usuario(a), <br/><br/>Nos permitimos comunicarle que los siguientes compromisos estan '+estado_nombre.nombre+'<br/><br/>'
							contenido+='Para dichos compromisos y en algunas ocasiones, usted es mencionado en los siguientes roles: '+rol+'.<br> Favor, tomar medidas segun su rol para cada compromiso<br/><br/>'
							contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
							contenido+='Gracias,<br/><br/><br/>'
							contenido+='Equipo SININ<br/>'
							contenido+=settings.EMAIL_HOST_USER+'<br/>'
							contenido+='<a href="'+settings.SERVER_URL+':'+settings.PORT_SERVER+'/usuario/">SININ</a><br/>'

							mail = Mensaje(
								remitente=settings.REMITENTE,
								destinatario=correo_envio,
								asunto='Compromisos '+ estado_nombre.nombre,
								contenido=contenido,
								appLabel='contrato',
								tieneAdjunto=True,
								adjunto=nombre_archivo,
								copia=''
							)
							mail.Send()
							# mail.simpleSend()
							if os.path.exists(nombre_archivo):
								os.remove(nombre_archivo)

					elif participante['tipo']=='externo':
						if estado == estadoC.por_vencer:
							comrposmisos_participante_externo = Compromiso.objects.filter(fecha_proximidad__lte=date1,estado__id=estado,responsable_interno=False,participante_responsable__id=int(participante['id'])).values(
									'id',
									'acta__consecutivo',
									'acta__usuario_organizador__persona__nombres','acta__usuario_organizador__persona__apellidos',
									'acta__controlador_actual__persona__nombres','acta__controlador_actual__persona__apellidos',
									'supervisor__persona__nombres','supervisor__persona__apellidos',
									'descripcion',
									'fecha_compromiso',
									'requiere_soporte',
									'responsable_interno',
									'participante_responsable__persona__nombres','participante_responsable__persona__apellidos',
									'usuario_responsable__persona__nombres','usuario_responsable__persona__apellidos')
						
						elif estado==estadoC.vencido:
							comrposmisos_participante_externo = Compromiso.objects.filter(fecha_compromiso__lte=date1,estado__id=estado,responsable_interno=False,participante_responsable__id=int(participante['id'])).values(
									'id',
									'acta__consecutivo',
									'acta__usuario_organizador__persona__nombres','acta__usuario_organizador__persona__apellidos',
									'acta__controlador_actual__persona__nombres','acta__controlador_actual__persona__apellidos',
									'supervisor__persona__nombres','supervisor__persona__apellidos',
									'descripcion',
									'fecha_compromiso',
									'requiere_soporte',
									'responsable_interno',
									'participante_responsable__persona__nombres','participante_responsable__persona__apellidos',
									'usuario_responsable__persona__nombres','usuario_responsable__persona__apellidos')

						if comrposmisos_participante_externo:

							correo_envio = correo_envio+participante['correo']+';'

							# INICIO - Crear el Excel
							# response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
							# response['Content-Disposition'] = 'attachment; filename="Reporte_contrato.xls"'

							# workbook = xlsxwriter.Workbook(response, {'in_memory': True})

							unique_filename = uuid.uuid4()
							nombre_archivo = '{}.xlsx'.format(unique_filename)
							workbook = xlsxwriter.Workbook(nombre_archivo)
							worksheet = workbook.add_worksheet('Contratos')

							worksheet.set_column('A:A', 10)
							worksheet.set_column('B:E', 25)
							worksheet.set_column('F:F', 30)
							worksheet.set_column('G:H', 10)

							format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
							format1.set_align('center')
							format1.set_align('vcenter')
							format2=workbook.add_format({'border':0})
							format5=workbook.add_format()
							format5.set_num_format('yyyy-mm-dd')

							row=1
							col=0

							worksheet.write('A1', 'No. acta', format1)
							worksheet.write('B1', 'Organizador', format1)
							worksheet.write('C1', 'Controlador', format1)
							worksheet.write('D1', 'Supervisor', format1)
							worksheet.write('E1', 'Responsable', format1)
							worksheet.write('F1', 'Descripción', format1)
							worksheet.write('G1', 'Fecha vencimiento', format1)
							worksheet.write('H1', 'Requiere soporte.', format1)

							

							for cont in comrposmisos_participante_externo:
								worksheet.write(row, col,cont['acta__consecutivo'],format2)
								worksheet.write(row, col+1,cont['acta__usuario_organizador__persona__nombres']+' '+cont['acta__usuario_organizador__persona__apellidos'],format2)
								worksheet.write(row, col+2,cont['acta__controlador_actual__persona__nombres']+' '+cont['acta__controlador_actual__persona__apellidos'],format2)
								worksheet.write(row, col+3,cont['supervisor__persona__nombres']+' '+cont['supervisor__persona__apellidos'],format2)
								

								if cont['responsable_interno']:
									worksheet.write(row, col+4,cont['usuario_responsable__persona__nombres']+' '+cont['usuario_responsable__persona__apellidos'],format2)
								else:
									worksheet.write(row, col+4,cont['participante_responsable__persona__nombres']+' '+cont['participante_responsable__persona__apellidos'],format2)

								worksheet.write(row, col+5,cont['descripcion'],format2)
								worksheet.write(row, col+6,cont['fecha_compromiso'],format5)

								if cont['requiere_soporte']:
									worksheet.write(row, col+7,'Si',format2)
								else:
									worksheet.write(row, col+7,'No',format2)

								row +=1
							workbook.close()

							estado_nombre = Estado.objects.get(pk=estado)
							contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
							contenido+='Estimado usuario(a), <br/><br/>Nos permitimos comunicarle que los siguientes compromisos estan '+estado_nombre.nombre+'<br/><br/>'
							contenido+='Para dichos compromisos y en algunas ocasiones, usted es mencionado en los siguientes roles: <br>1. responsable.<br> Favor, tomar medidas segun su rol para cada compromiso<br/><br/>'
							contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
							contenido+='Gracias,<br/><br/><br/>'
							contenido+='Equipo SININ<br/>'
							contenido+=settings.EMAIL_HOST_USER+'<br/>'
							contenido+='<a href="'+settings.SERVER_URL+':'+settings.PORT_SERVER+'/usuario/">SININ</a><br/>'

							mail = Mensaje(
								remitente=settings.REMITENTE,
								destinatario=correo_envio,
								asunto='Compromisos '+ estado_nombre.nombre,
								contenido=contenido,
								appLabel='contrato',
								tieneAdjunto=True,
								adjunto=nombre_archivo,
								copia=''
							)
							mail.Send()
							# mail.simpleSend()
							if os.path.exists(nombre_archivo):
								os.remove(nombre_archivo)
			

		# return JsonResponse({'message':'','success':'ok',
		# 				'data':participantes_notificadosAgrupados})
	except Exception as e:
		functions.toLog(e,'Tasks Notificaciones compromisos')