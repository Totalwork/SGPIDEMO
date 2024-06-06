# -*- coding: utf-8 -*- 
from coasmedas.celery import app
from django.conf import settings

from datetime import * 

from django.db.models import Max
from django.db import connection
import xlsxwriter
import uuid
import os
from .enumeration import correspondenciaRecibidaEstados

from adminMail.models import Mensaje

from correspondencia_recibida.models import CorrespondenciaRecibida,  CorrespondenciaRecibidaAsignada  
from correspondencia.models import CorrespondenciaEnviada , CorrespondenciaSoporte , CorrespondenciaConsecutivo 
from parametrizacion.models import Funcionario 
from usuario.models import Usuario , Persona 

from correspondencia_recibida.enumeration import Notificaciones

@app.task
def correspondenciaRecibidaSinSoporte():

	try:

		
		
		formato_fecha = "%Y-%m-%d"
		hoy = date.today()
		hoy = datetime.strptime(str(hoy), formato_fecha)	

		notificacion = Notificaciones()	

		funcionarios_notificar = Funcionario.objects.filter(notificaciones__id=notificacion.cartas_recibidas_sin_cargar_soporte ,activo=True)

		for f in funcionarios_notificar:

			try:
				empresaId = f.empresa_id								
				# # SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA Y NO SEAN COPIA
				queryHistorial = CorrespondenciaRecibidaAsignada.objects.filter(correspondenciaRecibida__empresa=empresaId, copia=False).values('correspondenciaRecibida_id').annotate(id=Max('id')).values('id')
				# #SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA Y SEAN DEL USUARIO BUSCADO POR LA PERSONA
				query_cartas_usuario_asigno = CorrespondenciaRecibidaAsignada.objects.filter(id__in = queryHistorial, usuario__persona_id = f.persona_id ).values('correspondenciaRecibida_id')
				
				queryset = CorrespondenciaRecibida.objects.filter(id__in=query_cartas_usuario_asigno)
				querySoporte = CorrespondenciaRecibidaSoporte.objects.filter(anulado = 0).values('correspondencia')# tipo uno correspondencia recibida
				queryset = queryset.exclude(correspondenciaRecibida_id__in = querySoporte).order_by('-correspondenciaRecibida__fechaRecibida','-correspondenciaRecibida__radicado')
				
				if queryset:
					contenido = ''
					correo_envio = ''
					correo_envio = f.persona.correo+';'

					#   # INICIO - Crear el Excel
					unique_filename = uuid.uuid4()

					ruta = settings.STATICFILES_DIRS[0]
					nombre_archivo = ruta+'\papelera\{}.xlsx'.format(unique_filename)    
					workbook = xlsxwriter.Workbook(nombre_archivo)
					worksheet = workbook.add_worksheet('radicasdos sin soporte')

					worksheet.set_column('A:D', 17)
					worksheet.set_column('E:E', 35)
					worksheet.set_column('F:F', 45)

					format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
					format1.set_align('center')
					format1.set_align('vcenter')
					format2=workbook.add_format({'border':0})
					format5=workbook.add_format()
					format5.set_num_format('yyyy-mm-dd')
					format_money=workbook.add_format({'border':False,
						'font_size':11,
						'bold':False,
						'valign':'vright',
						'num_format': '$#,##0'})

					row=1
					col=0

					worksheet.write('A1', 'Fecha Recibida', format1)
					worksheet.write('B1', 'Radicado', format1)
					worksheet.write('C1', 'Remitente', format1)
					worksheet.write('D1', 'Asunto', format1)

					for carta_recibida in queryset:
						meses = ''
						fecha = ''

						worksheet.write(row, col,carta_recibida.fechaRecibida,format5)
						worksheet.write(row, col+1,carta_recibida.radicado,format2)
						worksheet.write(row, col+2,carta_recibida.remitente,format2)
						worksheet.write(row, col+3,carta_recibida.asunto,format2)

						row +=1

					workbook.close()# FIN - Crear el Excel

					contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
					contenido+='Estimado usuario(a), <br/><br/>nos permitimos comunicarle que las siguientes cartas recibidas  estan <strong>sin soporte</strong>:<br/><br/>'
					contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
					contenido+='Gracias,<br/><br/><br/>'
					contenido+='Equipo SININ<br/>'
					contenido+='soporte@sinin.co<br/>'
					contenido+='<a href="http://52.42.43.115:8000/usuario/">SININ</a><br/>'

					mail = Mensaje(
						remitente=settings.REMITENTE,
						destinatario=correo_envio,
						asunto='Correspondencia recibida sin cargar soporte',
						contenido=contenido,
						appLabel='correspondencia',
						tieneAdjunto=True,
						adjunto=nombre_archivo,
						copia=''
					)
					mail.Send()
					# if os.path.exists(nombre_archivo):
					# 	os.remove(nombre_archivo)
			except Exception as e:
				raise e
			

	except Exception as e:
		print(e)

@app.task
def correspondenciaRecibidaSinRevisar():

	try:
		
		formato_fecha = "%Y-%m-%d"
		hoy = date.today()
		hoy = datetime.strptime(str(hoy), formato_fecha)		
		estado_c=estadoC()
		notificacion = Notificaciones()

		funcionarios_notificar = Funcionario.objects.filter(notificaciones=notificacion.cartas_recibidas_sin_revisar ,activo=True)

		for f in funcionarios_notificar:

			try:
				usuario_notificar = Usuario.objects.get(persona_id = f.persona_id , empresa_id = f.empresa_id)
				empresaId = f.empresa_id
				usuarioActual = usuario_notificar.id

				# SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA
				queryHistorial = CorrespondenciaRecibidaAsignada.objects.filter(correspondenciaRecibida__empresa = empresaId).values('correspondenciaRecibida_id').annotate(id=Max('id')).values('id')
				#SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA Y AL USUARIO QUE SE LE ASIGNO 
				queryset = CorrespondenciaRecibidaAsignada.objects.filter(id__in = queryHistorial , usuario = usuarioActual , copia = False, estado_id__in = [estado_c.por_Revisar, estado_c.reasignada])
				
				if queryset:
					correo_envio = ''
					contenido = ''
					correo_envio = f.persona.correo+';'

					#   # INICIO - Crear el Excel
					unique_filename = uuid.uuid4()

					ruta = settings.STATICFILES_DIRS[0]
					nombre_archivo = ruta+'\papelera\{}.xlsx'.format(unique_filename)    
					workbook = xlsxwriter.Workbook(nombre_archivo)
					worksheet = workbook.add_worksheet('radicados sin revisar')

					worksheet.set_column('A:D', 20)
					worksheet.set_column('E:E', 35)
					worksheet.set_column('F:F', 45)

					format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
					format1.set_align('center')
					format1.set_align('vcenter')
					format2=workbook.add_format({'border':0})
					format5=workbook.add_format()
					format5.set_num_format('yyyy-mm-dd')


					format_money=workbook.add_format({'border':False,
						'font_size':11,
						'bold':False,
						'valign':'vright',
						'num_format': '$#,##0'})

					row=1
					col=0

					worksheet.write('A1', 'Fecha Recibida', format1)
					worksheet.write('B1', unicode('Fecha Asignación', 'utf-8'), format1)
					worksheet.write('C1', unicode('No. de días radicada', 'utf-8'), format1)		
					worksheet.write('D1', 'Radicado', format1)
					worksheet.write('E1', 'Remitente', format1)
					worksheet.write('F1', 'Asunto', format1)

					for carta_recibida in queryset:
						meses = ''
						fecha = ''
					
						fechaasignar = carta_recibida.fechaAsignacion
						fechaasignar = str(fechaasignar.strftime('%Y-%m-%d %H:%M:%S'))

						worksheet.write(row, col,carta_recibida.correspondenciaRecibida.fechaRecibida,format5)
						worksheet.write(row, col+1,fechaasignar,format2)
						worksheet.write(row, col+2,carta_recibida.id,format2)
						worksheet.write(row, col+3,carta_recibida.correspondenciaRecibida.radicado,format2)
						worksheet.write(row, col+4,carta_recibida.correspondenciaRecibida.remitente,format2)
						worksheet.write(row, col+5,carta_recibida.correspondenciaRecibida.asunto,format2)

						row +=1

					workbook.close()# FIN - Crear el Excel

					contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
					contenido+='Estimado usuario(a), <br/><br/>nos permitimos comunicarle que las siguientes cartas recibidas  estan <strong>sin revisar</strong>:<br/><br/>'
					contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
					contenido+='Gracias,<br/><br/><br/>'
					contenido+='Equipo SININ<br/>'
					contenido+='soporte@sinin.co<br/>'
					contenido+='<a href="http://52.42.43.115:8000/usuario/">SININ</a><br/>'

					mail = Mensaje(
						remitente=settings.REMITENTE,
						destinatario=correo_envio,
						asunto='Correspondencia por revisar',
						contenido=contenido,
						appLabel='correspondencia',
						tieneAdjunto=True,
						adjunto=nombre_archivo,
						copia=''
					)
					mail.Send()
					# if os.path.exists(nombre_archivo):
					# 	os.remove(nombre_archivo)

			except Usuario.DoesNotExist as e:
				pass


	except Exception as e:
		print(e)

@app.task
def correspondenciaRecibidaSinResponder():

	try:
	
		formato_fecha = "%Y-%m-%d"
		hoy = date.today()
		hoy = datetime.strptime(str(hoy), formato_fecha)
		estado_c=estadoC()
		notificacion = Notificaciones()

		funcionarios_notificar = Funcionario.objects.filter(notificaciones=notificacion.correspondencia_recibida_sin_responder ,activo=True)

		for f in funcionarios_notificar:

			try:
				
				usuario_notificar = Usuario.objects.get(persona_id = f.persona_id , empresa_id = f.empresa_id)
				empresaId = f.empresa_id
				usuarioActual = usuario_notificar.id

				# SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA
				queryHistorial = CorrespondenciaRecibidaAsignada.objects.filter(correspondenciaRecibida__empresa=empresaId).values('correspondenciaRecibida_id').annotate(id=Max('id')).exclude(correspondenciaRecibida__fechaRespuesta__isnull=True).values("id")
				#SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA Y AL USUARIO QUE SE LE ASIGNO 
				queryset = CorrespondenciaRecibidaAsignada.objects.filter(id__in = queryHistorial , usuario = usuarioActual , copia = False , estado_id__in = [estado_c.por_Revisar, estado_c.reasignada])

				if queryset:
					correo_envio = ''
					contenido = ''
					correo_envio = f.persona.correo+';'

					#   # INICIO - Crear el Excel
					unique_filename = uuid.uuid4()

					ruta = settings.STATICFILES_DIRS[0]				
					nombre_archivo = ruta+'\papelera\{}.xlsx'.format(unique_filename)    
					workbook = xlsxwriter.Workbook(nombre_archivo)
					worksheet = workbook.add_worksheet('radicados sin responder')

					worksheet.set_column('A:D', 20)
					worksheet.set_column('E:E', 35)
					worksheet.set_column('F:F', 45)
					worksheet.set_column('G:G', 22)

					format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
					format1.set_align('center')
					format1.set_align('vcenter')
					format2=workbook.add_format({'border':0})
					format5=workbook.add_format()
					format5.set_num_format('yyyy-mm-dd')
					format6 = workbook.add_format({'num_format': 'dd/mm/yy hh:mm'})
					format_money=workbook.add_format({'border':False,
						'font_size':11,
						'bold':False,
						'valign':'vright',
						'num_format': '$#,##0'})

					row=1
					col=0

					worksheet.write('A1', 'Fecha Recibida', format1)
					worksheet.write('B1', unicode('Fecha Asignación', 'utf-8'), format1)
					worksheet.write('C1', unicode('No. de días radicada', 'utf-8'), format1)		
					worksheet.write('D1', 'Radicado', format1)
					worksheet.write('E1', 'Remitente', format1)
					worksheet.write('F1', 'Asunto', format1)
					worksheet.write('G1', 'Plazo de Respuesta', format1)

					for carta_recibida in queryset:
						meses = ''
						fecha = ''
						
						fechaasignar = carta_recibida.fechaAsignacion
						fechaasignar = str(fechaasignar.strftime('%Y-%m-%d %H:%M:%S'))
						fechaRecibida = carta_recibida.correspondenciaRecibida.fechaRecibida
						fechaRecibida = datetime.strptime(str(fechaRecibida), formato_fecha)
						diferencia_en_dias = hoy-fechaRecibida  # Resta las dos fechas
						dias=diferencia_en_dias.days


						worksheet.write(row, col,fechaRecibida,format5)
						worksheet.write(row, col+1, fechaasignar ,format6)
						worksheet.write(row, col+2,dias,format2)
						worksheet.write(row, col+3,carta_recibida.correspondenciaRecibida.radicado,format2)
						worksheet.write(row, col+4,carta_recibida.correspondenciaRecibida.remitente,format2)
						worksheet.write(row, col+5,carta_recibida.correspondenciaRecibida.asunto,format2)
						worksheet.write(row, col+6,carta_recibida.correspondenciaRecibida.fechaRespuesta,format5)

						row +=1

					workbook.close()# FIN - Crear el Excel

					contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
					contenido+='Estimado usuario(a), <br/><br/>nos permitimos comunicarle que las siguientes cartas recibidas  estan <strong>sin responder</strong>:<br/><br/>'
					contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
					contenido+='Gracias,<br/><br/><br/>'
					contenido+='Equipo SININ<br/>'
					contenido+='soporte@sinin.co<br/>'
					contenido+='<a href="http://52.42.43.115:8000/usuario/">SININ</a><br/>'

					mail = Mensaje(
						remitente=settings.REMITENTE,
						destinatario=correo_envio,
						asunto='Correspondencia sin responder',
						contenido=contenido,
						appLabel='correspondencia',
						tieneAdjunto=True,
						adjunto=nombre_archivo,
						copia=''
					)
					mail.Send()
					# if os.path.exists(nombre_archivo):
					# 	os.remove(nombre_archivo)
			except Exception as e:
				raise e
			

	except Exception as e:
		print(e)