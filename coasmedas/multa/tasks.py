# -*- coding: utf-8 -*- 
from coasmedas.celery import app
from django.conf import settings

from datetime import *

# import time
from django.db.models import Max
from django.db import connection
import xlsxwriter
import uuid
import os
from django.db.models import Q
from adminMail.models import Mensaje
from multa.enumeration import EstadoMulta , Notificaciones

from proyecto.models import Proyecto
from correspondencia.models import CorrespondenciaEnviada , CorrespondenciaSoporte , CorrespondenciaConsecutivo 
from parametrizacion.models import Funcionario 
from multa.models import SolicitudConsecutivo , ConjuntoEvento , Evento , Solicitud , SolicitudEmpresa , SolicitudEvento , SolicitudHistorial , SolicitudSoporte , SolicitudApelacion , SolicitudPronunciamiento
from contrato.models import EmpresaContrato

# MULTAS NOTIFICADAS PLAZO POR VENCER
@app.task
def multasNotificadasPorVencer():
	try:
		
		formato_fecha = "%Y-%m-%d"
		hoy = date.today()
		hoy = datetime.strptime(str(hoy), formato_fecha)

		notificacion = Notificaciones()

		funcionarios_notificar = Funcionario.objects.filter(notificaciones = notificacion.multas_notificadas_contratista_plazo_por_vencer_o_vencido ,activo=True)


		for f in funcionarios_notificar:

			empresaId = f.empresa_id
			
			# consulta de todos los proyectos que es responsable un funcionario
			proyecto_funcionario = Proyecto.funcionario.through.objects.filter(funcionario_id = f.id ).values_list('proyecto_id')
			# consulta todos los contratos asociados a un proyecto
			proyecto_contrato = Proyecto.contrato.through.objects.filter(proyecto_id__in = proyecto_funcionario).values_list('contrato_id')

			queryset_empresa = SolicitudEmpresa.objects.filter(empresa_id = empresaId,
				solicitud__contrato__id__in = proyecto_contrato
				).values_list('solicitud_id', flat=True)


			queryHistorial = SolicitudHistorial.objects.filter(solicitud_id__in = queryset_empresa).values('solicitud_id').annotate(id=Max('id')).values("id")
		
			qset = ( Q(solicitud__fk_Solicitud_SolicitudHistorial__id__in = queryHistorial) )

			es=EstadoMulta()
			qset = qset & ( Q(solicitud__fk_Solicitud_SolicitudHistorial__estado_id__in = [
					es.notificada_contratista
				]))			
			
			dias_3 = timedelta(days=3)
			dias_5 = timedelta(days=5)

			hoy_mas_3_dia = hoy-dias_3
			hoy_mas_5_dia = hoy-dias_5

			qset = qset & ( Q(solicitud__fk_Solicitud_SolicitudHistorial__fecha__gte = hoy_mas_5_dia ) )
			qset = qset & ( Q(solicitud__fk_Solicitud_SolicitudHistorial__fecha__lte = hoy_mas_3_dia)  )


			queryset = SolicitudEmpresa.objects.filter(qset)

			solicitudes = []
			for	s in queryset:
				verificar = esSoloLectura(s.solicitud.contrato, f.empresa.id)
				if verificar == False:
					solicitudes.append(s)

			if solicitudes.count() > 0:
				
				correo_envio = ''
				contenido = ''
				correo_envio = f.persona.correo+';'

				#   # INICIO - Crear el Excel
				unique_filename = uuid.uuid4()
				ruta = settings.STATICFILES_DIRS[0]
				nombre_archivo = ruta+'\papelera\{}.xlsx'.format(unique_filename)    
				workbook = xlsxwriter.Workbook(nombre_archivo)
				worksheet = workbook.add_worksheet('Correspondencias sin soporte')

				worksheet.set_column('A:A', 25)
				worksheet.set_column('B:B', 15)
				worksheet.set_column('C:D', 50)
				worksheet.set_column('E:E', 35)
				worksheet.set_column('F:F', 45)
				worksheet.set_column('G:G', 45)

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

				worksheet.write('A1', 'Consecutivo multa', format1)
				worksheet.write('B1', 'Fecha notificacion al contratista', format1)
				worksheet.write('C1', 'Solicitante', format1)
				worksheet.write('D1', 'No Contrato', format1)
				worksheet.write('E1', 'Contrato', format1)
				worksheet.write('F1', 'Contratista', format1)
				worksheet.write('G1', 'Valor multa', format1)


				for objecto in solicitudes:

					meses = ''
					fecha = ''

					solicitante = SolicitudEmpresa.objects.get(solicitud_id = objecto.solicitud.id , propietario = True)
					fecha_notificacion_contratista = SolicitudHistorial.objects.get(solicitud_id = objecto.solicitud.id , estado_id = es.notificada_contratista)

					worksheet.write(row, col  ,objecto.solicitud.consecutivo,format2)
					worksheet.write(row, col+1,str(fecha_notificacion_contratista.fecha) ,format5)
					worksheet.write(row, col+2, solicitante.empresa.nombre ,format2)
					worksheet.write(row, col+3,objecto.solicitud.contrato.numero,format2)
					worksheet.write(row, col+4,objecto.solicitud.contrato.nombre,format2)
					worksheet.write(row, col+5,objecto.solicitud.contrato.contratista.nombre,format2)
					worksheet.write(row, col+6,objecto.solicitud.valorImpuesto,format_money)

					row +=1

				workbook.close()# FIN - Crear el Excel


				contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
				contenido+='Estimado usuario(a), <br/><br/>nos permitimos comunicarle que las siguientes multas estan por <strong>exceder</strong> el plazo de los  5 dias habiles para su imposicion :<br/><br/>'
				contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
				contenido+='Gracias,<br/><br/><br/>'
				contenido+='Equipo SININ<br/>'
				contenido+='soporte@sinin.co<br/>'
				contenido+='<a href="http://52.42.43.115:8000/usuario/">SININ</a><br/>'

				mail = Mensaje(
					remitente=settings.REMITENTE,
					destinatario=correo_envio,
					asunto='Multas - solicitudes por exceder el plazo limite de  imposicion de multa',
					contenido=contenido,
					appLabel='multas',
					tieneAdjunto=True,
					adjunto=nombre_archivo,
					copia=''
				)

				mail.Send()

				if os.path.exists(nombre_archivo):
					os.remove(nombre_archivo)


	except Exception as e:
		raise e


# MULTAS PLAZO VENCIDO
# @app.task
# def multasNotificadasVencidas():
# 	try:
		
		
# 		formato_fecha = "%Y-%m-%d"
# 		hoy = date.today()
# 		hoy = datetime.strptime(str(hoy), formato_fecha)

# 		notificacion = Notificaciones()

# 		funcionarios_notificar = Funcionario.objects.filter(notificaciones = notificacion.multas_notificadas_contratista_plazo_por_vencer_o_vencido)


# 		for f in funcionarios_notificar:
			
# 			empresaId = f.empresa_id

# 			# consulta de todos los proyectos que es responsable un funcionario
# 			proyecto_funcionario = Proyecto.funcionario.through.objects.filter(funcionario_id = f.id ).values_list('proyecto_id')
# 			# consulta todos los contratos asociados a un proyecto
# 			proyecto_contrato = Proyecto.contrato.through.objects.filter(proyecto_id__in = proyecto_funcionario).values_list('contrato_id')

# 			queryset_empresa = SolicitudEmpresa.objects.filter(empresa_id = empresaId,
# 				solicitud__contrato__id__in = proyecto_contrato
# 				).values_list('solicitud_id', flat=True)

# 			queryHistorial = SolicitudHistorial.objects.filter(solicitud_id__in = queryset_empresa).values('solicitud_id').annotate(id=Max('id')).values("id")

		
# 			qset = ( Q(solicitud__fk_Solicitud_SolicitudHistorial__id__in = queryHistorial) )

# 			es=EstadoMulta()
# 			qset = qset & ( Q(solicitud__fk_Solicitud_SolicitudHistorial__estado_id__in = [
# 					es.notificada_contratista
# 				]))

# 			dias_6 = timedelta(days=6)
# 			hoy_menos_6_dia = hoy-dias_6

# 			qset = qset & ( Q(solicitud__fk_Solicitud_SolicitudHistorial__fecha__lte = hoy_menos_6_dia)  )
# 			qset = qset & (Q(empresa_id = empresaId))

# 			queryset = SolicitudEmpresa.objects.filter(qset)

# 			if queryset:

# 				correo_envio = ''
# 				contenido = ''
# 				correo_envio = f.persona.correo+';'

# 				#   # INICIO - Crear el Excel
# 				unique_filename = uuid.uuid4()
# 				ruta = settings.STATICFILES_DIRS[0]
# 				nombre_archivo = ruta+'\papelera\{}.xlsx'.format(unique_filename)    
# 				workbook = xlsxwriter.Workbook(nombre_archivo)
# 				worksheet = workbook.add_worksheet('Correspondencias sin soporte')

# 				worksheet.set_column('A:A', 25)
# 				worksheet.set_column('B:B', 15)
# 				worksheet.set_column('C:D', 50)
# 				worksheet.set_column('E:E', 35)
# 				worksheet.set_column('F:F', 45)
# 				worksheet.set_column('G:G', 45)

# 				format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
# 				format1.set_align('center')
# 				format1.set_align('vcenter')
# 				format2=workbook.add_format({'border':0})
# 				format5=workbook.add_format()
# 				format5.set_num_format('yyyy-mm-dd')
# 				format_money=workbook.add_format({'border':False,
# 					'font_size':11,
# 					'bold':False,
# 					'valign':'vright',
# 					'num_format': '$#,##0'})

# 				row=1
# 				col=0

# 				worksheet.write('A1', 'Consecutivo multa', format1)
# 				worksheet.write('B1', 'Fecha notificacion al contratista', format1)
# 				worksheet.write('C1', 'Solicitante', format1)
# 				worksheet.write('D1', 'No Contrato', format1)
# 				worksheet.write('E1', 'Contrato', format1)
# 				worksheet.write('F1', 'Contratista', format1)
# 				worksheet.write('G1', 'Valor multa', format1)


# 				for objecto in queryset:

# 					meses = ''
# 					fecha = ''

# 					solicitante = SolicitudEmpresa.objects.get(solicitud_id = objecto.solicitud.id , propietario = True)
# 					fecha_notificacion_contratista = SolicitudHistorial.objects.get(solicitud_id = objecto.solicitud.id , estado_id = es.notificada_contratista)

# 					worksheet.write(row, col  ,objecto.solicitud.consecutivo,format2)
# 					worksheet.write(row, col+1,str(fecha_notificacion_contratista.fecha) ,format5)
# 					worksheet.write(row, col+2, solicitante.empresa.nombre ,format2)
# 					worksheet.write(row, col+3,objecto.solicitud.contrato.numero,format2)
# 					worksheet.write(row, col+4,objecto.solicitud.contrato.nombre,format2)
# 					worksheet.write(row, col+5,objecto.solicitud.contrato.contratista.nombre,format2)
# 					worksheet.write(row, col+6,objecto.solicitud.valorImpuesto,format_money)

# 					row +=1

# 				workbook.close()# FIN - Crear el Excel


# 				contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
# 				contenido+='Estimado usuario(a), <br/><br/>nos permitimos comunicarle que las siguientes multas han <strong >excedido</strong> los 5 dias de plazo para su imposicion :<br/><br/>'
# 				contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
# 				contenido+='Gracias,<br/><br/><br/>'
# 				contenido+='Equipo SININ<br/>'
# 				contenido+='soporte@sinin.co<br/>'
# 				contenido+='<a href="http://52.42.43.115:8000/usuario/">SININ</a><br/>'

# 				mail = Mensaje(
# 					remitente=settings.REMITENTE,
# 					destinatario=correo_envio,
# 					asunto='Multas - solicitudes que excedieron el plazo limite de  imposicion de multa',
# 					contenido=contenido,
# 					appLabel='multas',
# 					tieneAdjunto=True,
# 					adjunto=nombre_archivo,
# 					copia=''
# 				)

# 				mail.Send()

# 				if os.path.exists(nombre_archivo):
# 					os.remove(nombre_archivo)


# 	except Exception as e:
# 		raise e


# MULTAS CONFIRMADAS SIN REGISTRO OF
@app.task
def multasConfirmadasSinRegistroOf():
	try:
		
		
		formato_fecha = "%Y-%m-%d"
		hoy = date.today()
		hoy = datetime.strptime(str(hoy), formato_fecha)

		notificacion = Notificaciones()

		funcionarios_notificar = Funcionario.objects.filter(notificaciones = notificacion.multas_confirmadas_o_modificadas_sin_registro_of ,activo=True)


		for f in funcionarios_notificar:
			
			empresaId = f.empresa_id
			
			# consulta de todos los proyectos que es responsable un funcionario
			proyecto_funcionario = Proyecto.funcionario.through.objects.filter(funcionario_id = f.id ).values_list('proyecto_id')
			# consulta todos los contratos asociados a un proyecto
			proyecto_contrato = Proyecto.contrato.through.objects.filter(proyecto_id__in = proyecto_funcionario).values_list('contrato_id')

			queryset_empresa = SolicitudEmpresa.objects.filter(empresa_id = empresaId,
				solicitud__contrato__id__in = proyecto_contrato
				).values_list('solicitud_id', flat=True)

			queryHistorial = SolicitudHistorial.objects.filter(solicitud_id__in = queryset_empresa).values('solicitud_id').annotate(id=Max('id')).values("id")
		
			qset = ( Q(solicitud__fk_Solicitud_SolicitudHistorial__id__in = queryHistorial) )

			es=EstadoMulta()
			qset = qset & ( Q(solicitud__fk_Solicitud_SolicitudHistorial__estado_id__in = [
					es.confirmada
				]))

			qset = qset & ( Q(solicitud__codigoOF__isnull = True ) |  Q(solicitud__codigoOF = None ) )


			queryset = SolicitudEmpresa.objects.filter(qset)

			solicitudes = []
			for	s in queryset:
				verificar = esSoloLectura(s.solicitud.contrato, f.empresa.id)
				if verificar == False:
					solicitudes.append(s)

			if solicitudes:
				correo_envio = ''
				contenido = ''
				correo_envio = f.persona.correo+';'

				#   # INICIO - Crear el Excel
				unique_filename = uuid.uuid4()
				ruta = settings.STATICFILES_DIRS[0]
				nombre_archivo = ruta+'\papelera\{}.xlsx'.format(unique_filename)    
				workbook = xlsxwriter.Workbook(nombre_archivo)
				worksheet = workbook.add_worksheet('Correspondencias sin soporte')

				worksheet.set_column('A:A', 25)
				worksheet.set_column('B:B', 15)
				worksheet.set_column('C:D', 50)
				worksheet.set_column('E:E', 35)
				worksheet.set_column('F:F', 45)
				worksheet.set_column('G:G', 45)

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

				worksheet.write('A1', 'Consecutivo multa', format1)
				worksheet.write('B1', 'Fecha notificacion al contratista', format1)
				worksheet.write('C1', 'Solicitante', format1)
				worksheet.write('D1', 'No Contrato', format1)
				worksheet.write('E1', 'Contrato', format1)
				worksheet.write('F1', 'Contratista', format1)
				worksheet.write('G1', 'Valor multa', format1)


				for objecto in solicitudes:

					meses = ''
					fecha = ''

					solicitante = SolicitudEmpresa.objects.get(solicitud_id = objecto.solicitud.id , propietario = True)
					fecha_notificacion_contratista = SolicitudHistorial.objects.get(solicitud_id = objecto.solicitud.id , estado_id = es.notificada_contratista)

					worksheet.write(row, col  ,objecto.solicitud.consecutivo,format2)
					worksheet.write(row, col+1,str(fecha_notificacion_contratista.fecha) ,format5)
					worksheet.write(row, col+2, solicitante.empresa.nombre ,format2)
					worksheet.write(row, col+3,objecto.solicitud.contrato.numero,format2)
					worksheet.write(row, col+4,objecto.solicitud.contrato.nombre,format2)
					worksheet.write(row, col+5,objecto.solicitud.contrato.contratista.nombre,format2)
					worksheet.write(row, col+6,objecto.solicitud.valorImpuesto,format_money)

					row +=1

				workbook.close()# FIN - Crear el Excel


				contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
				contenido+='Estimado usuario(a), <br/><br/>nos permitimos comunicarle que las siguientes multas no tienen  el <strong >registro orden de operacion</strong> <br/><br/>'
				contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
				contenido+='Gracias,<br/><br/><br/>'
				contenido+='Equipo SININ<br/>'
				contenido+='soporte@sinin.co<br/>'
				contenido+='<a href="http://52.42.43.115:8000/usuario/">SININ</a><br/>'

				mail = Mensaje(
					remitente=settings.REMITENTE,
					destinatario=correo_envio,
					asunto='Multas - solicitudes sin registro OF',
					contenido=contenido,
					appLabel='multas',
					tieneAdjunto=True,
					adjunto=nombre_archivo,
					copia=''
				)

				mail.Send()

				if os.path.exists(nombre_archivo):
					os.remove(nombre_archivo)



	except Exception as e:
		raise e

# MULTAS PARA CONTABILIZAR
@app.task
def multasParaContabilizar():
	try:
		
		
		formato_fecha = "%Y-%m-%d"
		hoy = date.today()
		hoy = datetime.strptime(str(hoy), formato_fecha)

		notificacion = Notificaciones()

		funcionarios_notificar = Funcionario.objects.filter(notificaciones = notificacion.multas_pendientes_por_contabilizar ,activo=True)


		for f in funcionarios_notificar:
			
			empresaId = f.empresa_id
			
			# consulta de todos los proyectos que es responsable un funcionario
			proyecto_funcionario = Proyecto.funcionario.through.objects.filter(funcionario_id = f.id ).values_list('proyecto_id')
			# consulta todos los contratos asociados a un proyecto
			proyecto_contrato = Proyecto.contrato.through.objects.filter(proyecto_id__in = proyecto_funcionario).values_list('contrato_id')

			queryset_empresa = SolicitudEmpresa.objects.filter(empresa_id = empresaId,
				solicitud__contrato__id__in = proyecto_contrato
				).values_list('solicitud_id', flat=True)


			queryHistorial = SolicitudHistorial.objects.filter(solicitud_id__in = queryset_empresa).values('solicitud_id').annotate(id=Max('id')).values("id")
		
			qset =  ( Q(solicitud__fk_Solicitud_SolicitudHistorial__id__in = queryHistorial) )

			es=EstadoMulta()
			qset = qset & ( Q(solicitud__fk_Solicitud_SolicitudHistorial__estado_id__in = [
					es.pendiente_contabilizacion
				]))


			queryset = SolicitudEmpresa.objects.filter(qset)

			solicitudes = []
			for	s in queryset:
				verificar = esSoloLectura(s.solicitud.contrato, f.empresa.id)
				if verificar == False:
					solicitudes.append(s)

			if solicitudes:
				
				correo_envio = ''
				contenido = ''
				correo_envio = f.persona.correo+';'

				#   # INICIO - Crear el Excel
				unique_filename = uuid.uuid4()
				ruta = settings.STATICFILES_DIRS[0]
				nombre_archivo = ruta+'\papelera\{}.xlsx'.format(unique_filename)    
				workbook = xlsxwriter.Workbook(nombre_archivo)
				worksheet = workbook.add_worksheet('Correspondencias sin soporte')

				worksheet.set_column('A:A', 25)
				worksheet.set_column('B:B', 15)
				worksheet.set_column('C:D', 50)
				worksheet.set_column('E:E', 35)
				worksheet.set_column('F:F', 45)
				worksheet.set_column('G:G', 45)

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

				worksheet.write('A1', 'Consecutivo multa', format1)
				worksheet.write('B1', 'Fecha notificacion al contratista', format1)
				worksheet.write('C1', 'Solicitante', format1)
				worksheet.write('D1', 'No Contrato', format1)
				worksheet.write('E1', 'Contrato', format1)
				worksheet.write('F1', 'Contratista', format1)
				worksheet.write('G1', 'Valor multa', format1)




				for objecto in solicitudes:

					meses = ''
					fecha = ''

					solicitante = SolicitudEmpresa.objects.get(solicitud_id = objecto.solicitud.id , propietario = True)
					fecha_notificacion_contratista = SolicitudHistorial.objects.get(solicitud_id = objecto.solicitud.id , estado_id = es.notificada_contratista)

					worksheet.write(row, col  ,objecto.solicitud.consecutivo,format2)
					worksheet.write(row, col+1,str(fecha_notificacion_contratista.fecha) ,format5)
					worksheet.write(row, col+2, solicitante.empresa.nombre ,format2)
					worksheet.write(row, col+3,objecto.solicitud.contrato.numero,format2)
					worksheet.write(row, col+4,objecto.solicitud.contrato.nombre,format2)
					worksheet.write(row, col+5,objecto.solicitud.contrato.contratista.nombre,format2)
					worksheet.write(row, col+6,objecto.solicitud.valorImpuesto,format_money)

					row +=1

				workbook.close()# FIN - Crear el Excel


				contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
				contenido+='Estimado usuario(a), <br/><br/>nos permitimos comunicarle que las siguientes multas estan pendientes por <strong>contabilizar</strong> <br/><br/>'
				contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
				contenido+='Gracias,<br/><br/><br/>'
				contenido+='Equipo SININ<br/>'
				contenido+='soporte@sinin.co<br/>'
				contenido+='<a href="http://52.42.43.115:8000/usuario/">SININ</a><br/>'

				mail = Mensaje(
					remitente=settings.REMITENTE,
					destinatario=correo_envio,
					asunto='Multas - solicitudes para contabilizar',
					contenido=contenido,
					appLabel='multas',
					tieneAdjunto=True,
					adjunto=nombre_archivo,
					copia=''
				)

				mail.Send()

				if os.path.exists(nombre_archivo):
					os.remove(nombre_archivo)



	except Exception as e:
		raise e



# MULTAS EN ESTADOS PRE-CONFIRMADAS
@app.task
def multasPorConfirmar():
	try:
		
		
		formato_fecha = "%Y-%m-%d"
		hoy = date.today()
		hoy = datetime.strptime(str(hoy), formato_fecha)
		notificacion = Notificaciones()
		funcionarios_notificar = Funcionario.objects.filter(notificaciones = notificacion.multas_pre_confirmadas ,activo=True)


		for f in funcionarios_notificar:
			
			empresaId = f.empresa_id
			# consulta de todos los proyectos que es responsable un funcionario
			proyecto_funcionario = Proyecto.funcionario.through.objects.filter(funcionario_id = f.id ).values_list('proyecto_id')
			# consulta todos los contratos asociados a un proyecto
			proyecto_contrato = Proyecto.contrato.through.objects.filter(proyecto_id__in = proyecto_funcionario).values_list('contrato_id')

			queryset_empresa = SolicitudEmpresa.objects.filter(empresa_id = empresaId,
				solicitud__contrato__id__in = proyecto_contrato
				).values_list('solicitud_id', flat=True)

			queryHistorial = SolicitudHistorial.objects.filter(solicitud_id__in = queryset_empresa).values('solicitud_id').annotate(id=Max('id')).values("id")

		
			qset = ( Q(solicitud__fk_Solicitud_SolicitudHistorial__id__in = queryHistorial) )

			es=EstadoMulta()
			qset = qset & ( Q(solicitud__fk_Solicitud_SolicitudHistorial__estado_id__in = [es.preconfirmadas]))

			qset = qset & (Q(empresa_id = empresaId))

			queryset = SolicitudEmpresa.objects.filter(qset)

			solicitudes = []
			for	s in queryset:
				verificar = esSoloLectura(s.solicitud.contrato, f.empresa.id)
				if verificar == False:
					solicitudes.append(s)

			if solicitudes.count() > 0:

				correo_envio = ''
				contenido = ''
				correo_envio = f.persona.correo+';'

				#   # INICIO - Crear el Excel
				unique_filename = uuid.uuid4()
				ruta = settings.STATICFILES_DIRS[0]
				nombre_archivo = ruta+'\papelera\{}.xlsx'.format(unique_filename)    
				workbook = xlsxwriter.Workbook(nombre_archivo)
				worksheet = workbook.add_worksheet('Correspondencias sin soporte')

				worksheet.set_column('A:A', 25)
				worksheet.set_column('B:B', 15)
				worksheet.set_column('C:D', 50)
				worksheet.set_column('E:E', 35)
				worksheet.set_column('F:F', 45)
				worksheet.set_column('G:G', 45)

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

				worksheet.write('A1', 'Consecutivo multa', format1)
				worksheet.write('B1', 'Fecha notificacion al contratista', format1)
				worksheet.write('C1', 'Solicitante', format1)
				worksheet.write('D1', 'No Contrato', format1)
				worksheet.write('E1', 'Contrato', format1)
				worksheet.write('F1', 'Contratista', format1)
				worksheet.write('G1', 'Valor multa', format1)


				for objecto in solicitudes:

					meses = ''
					fecha = ''

					solicitante = SolicitudEmpresa.objects.get(solicitud_id = objecto.solicitud.id , propietario = True)
					fecha_notificacion_contratista = SolicitudHistorial.objects.get(solicitud_id = objecto.solicitud.id , estado_id = es.notificada_contratista)

					worksheet.write(row, col  ,objecto.solicitud.consecutivo,format2)
					worksheet.write(row, col+1,str(fecha_notificacion_contratista.fecha) ,format5)
					worksheet.write(row, col+2, solicitante.empresa.nombre ,format2)
					worksheet.write(row, col+3,objecto.solicitud.contrato.numero,format2)
					worksheet.write(row, col+4,objecto.solicitud.contrato.nombre,format2)
					worksheet.write(row, col+5,objecto.solicitud.contrato.contratista.nombre,format2)
					worksheet.write(row, col+6,objecto.solicitud.valorImpuesto,format_money)

					row +=1

				workbook.close()# FIN - Crear el Excel


				contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
				contenido+='Estimado usuario(a), <br/><br/>nos permitimos comunicarle que las siguientes multas han <strong >excedido</strong> los 5 dias de plazo para su imposicion :<br/><br/>'
				contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
				contenido+='Gracias,<br/><br/><br/>'
				contenido+='Equipo SININ<br/>'
				contenido+='soporte@sinin.co<br/>'
				contenido+='<a href="http://52.42.43.115:8000/usuario/">SININ</a><br/>'

				mail = Mensaje(
					remitente=settings.REMITENTE,
					destinatario=correo_envio,
					asunto='Multas por confirmar- solicitudes que excedieron el plazo limite de  imposicion de multa',
					contenido=contenido,
					appLabel='multas',
					tieneAdjunto=True,
					adjunto=nombre_archivo,
					copia=''
				)

				mail.Send()

				if os.path.exists(nombre_archivo):
					os.remove(nombre_archivo)


	except Exception as e:
		raise e


# ACTUALIZAR ESTADOS
# MULTAS EN ESTADOS PRE-CONFIRMADASNOTIFICADAS AL CONTRATISTA
@app.task
def multasUpdatePreconfirmadas():
	try:	
		
		formato_fecha = "%Y-%m-%d"
		hoy = date.today()
		hoy = datetime.strptime(str(hoy), formato_fecha)
		# ahora = time.strftime("%c")
		queryHistorial = SolicitudHistorial.objects.filter().values('solicitud_id').annotate(id=Max('id')).values("id")

		qset = ( Q(id__in = queryHistorial) )
		es=EstadoMulta()
		qset = qset & ( Q(estado_id__in = [ es.notificada_contratista ]))
		dias_6 = timedelta(days=6)
		hoy_menos_6_dia = hoy-dias_6
		qset = qset & ( Q(fecha__lte = hoy_menos_6_dia)  )

		queryset = SolicitudHistorial.objects.filter(qset)

		insert_list = []
		for item in queryset:
			insert_list.append(
				SolicitudHistorial(fecha=hoy
									,solicitud_id=item.solicitud.id
									,estado_id=es.preconfirmadas
									,usuario_id=251#usuario de maria auxiliadora bornacelli
									,comentarios='multa actualizada por el sistema')
				)
		
		SolicitudHistorial.objects.bulk_create(insert_list)
	except Exception as e:
		raise e

# MULTAS EN ESTADOS PRE-CONFIRMADAS
@app.task
def multasUpdateConfirmadas():
	try:		
		formato_fecha = "%Y-%m-%d"
		hoy = date.today()
		hoy = datetime.strptime(str(hoy), formato_fecha)

		queryHistorial = SolicitudHistorial.objects.filter().values('solicitud_id').annotate(id=Max('id')).values("id")
		qset = ( Q(id__in = queryHistorial) )
		es=EstadoMulta()
		qset = qset & ( Q(estado_id__in = [es.preconfirmadas]))
		dias_5 = timedelta(days=5)
		hoy_menos_5_dia = hoy-dias_5
		qset = qset & ( Q(fecha__lte = hoy_menos_5_dia)  )

		queryset = SolicitudHistorial.objects.filter(qset)

		insert_list = []
		for item in queryset:
			insert_list.append(
				SolicitudHistorial(fecha=hoy
									,solicitud_id=item.solicitud.id
									,estado_id=es.confirmada
									,usuario_id=251#usuario de maria auxiliadora bornacelli
									,comentarios='multa actualizada por el sistema')
				)
		
		SolicitudHistorial.objects.bulk_create(insert_list)

	except Exception as e:
		raise e


def esSoloLectura(contratoObj, empresa):
	if contratoObj.mcontrato:
		contrato = contratoObj.mcontrato.id
	else:
		contrato = contratoObj.id

	empresaContrato = EmpresaContrato.objects.filter(contrato__id=contrato, empresa__id=empresa).first()
	soloLectura = False if empresaContrato is not None and empresaContrato.edita else True
	return soloLectura