from sinin4.celery import app
from django.db import connection
from .models import Diseno,DVersionesDiseno
from usuario.models import Usuario
from parametrizacion.models import Notificacion
from adminMail.models import Mensaje
from django.conf import settings
from datetime import *

from sinin4.functions import functions

@app.task
def envioNotificacionReporteProyecto(version_diseno_id,empresa):
	try:
		cursor = connection.cursor()
		cursor.callproc('[dbo].[seguridad_social_personas_notificar]',[44,])
		columns = cursor.description 
		LisCorreos = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]

		correo_copia=""
		list_copia=Notificacion.objects.get(pk=44)

		for item in list_copia.usuario_cc.all():
			print(item.correo)
			if correo_copia=='':
				correo_copia=item.correo+';'
			else:
				correo_copia=correo_copia+item.correo+';'

		correo_envio=''
		for p in LisCorreos:
			if correo_envio=='':
				correo_envio=p['correo']+';'
			else:
				correo_envio=correo_envio+p['correo']+';'

		sql_diseno=DVersionesDiseno.objects.get(pk=version_diseno_id)

		contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
		contenido = contenido + "Estimado usuario(a),<br /><br /> Env&iacute;o para su informaci&oacute;n, el Proyecto <strong>"+sql_diseno.diseno.nombre+"</strong> de la version <strong>"+sql_diseno.nombre+"</strong> del departamento <strong>"+sql_diseno.diseno.municipio.departamento.nombre+"</strong> del municipio <strong>"+sql_diseno.diseno.municipio.nombre+"</strong> ";		
		contenido = contenido + "de la campa&ntildea <strong>"+sql_diseno.diseno.campana.nombre+"</strong>, se encuentra cargado por el dise&ntildeador <strong>"+empresa+"</strong>";
		contenido = contenido + '<br /><br /><br />Favor no responder este correo, es de uso informativo unicamente.<br /><br /><br />Gracias,<br /><br /><br />'
		contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'

		mail = Mensaje(
					remitente=settings.REMITENTE,
					destinatario=correo_envio,
					asunto='Notificacion de informacion cargada en Proyecto de Gestion',
					contenido=contenido,
					appLabel='gestion de Proyecto',
					copia=correo_copia
					)	

		mail.Send()

	except Exception as e:
		print(e)


@app.task
def envioNotificacionReporteExitoso(version_diseno_id,empresa,usuario):
	try:
		cursor = connection.cursor()
		cursor.callproc('[dbo].[seguridad_social_personas_notificar]',[45,])
		columns = cursor.description 
		LisCorreos = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]

		correo_envio=''
		for p in LisCorreos:
			if correo_envio=='':
				correo_envio=p['correo']+';'
			else:
				correo_envio=correo_envio+p['correo']+';'

		sql_diseno=DVersionesDiseno.objects.get(pk=version_diseno_id)

		contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
		contenido = contenido + "Estimado usuario(a),<br /><br /> La informaci&oacute;n del Proyecto <strong>"+sql_diseno.diseno.nombre+"</strong> de la version <strong>"+sql_diseno.nombre+"</strong> del departamento <strong>"+sql_diseno.diseno.municipio.departamento.nombre+"</strong> del municipio <strong>"+sql_diseno.diseno.municipio.nombre+"</strong> ";		
		contenido = contenido + "de la campa&ntildea <strong>"+sql_diseno.diseno.campana.nombre+"</strong>, ha sido recibida y revisada a satisfaccion por el usuario <strong>"+usuario+"</strong> de la empresa <strong>"+empresa+"</strong>";
		contenido = contenido + '<br /><br /><br />Favor no responder este correo, es de uso informativo unicamente.<br /><br /><br />Gracias,<br /><br /><br />'
		contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'

		mail = Mensaje(
					remitente=settings.REMITENTE,
					destinatario=correo_envio,
					asunto='Notificacion de  informacion recibida en Proyecto de Gestion',
					contenido=contenido,
					appLabel='gestion de Proyecto'
					)	

		mail.simpleSend()

	except Exception as e:
		print(e)


@app.task
def envioNotificacionReporteInsconsitencia(version_diseno_id,empresa,usuario,comentario):
	try:
		cursor = connection.cursor()
		cursor.callproc('[dbo].[seguridad_social_personas_notificar]',[45,])
		columns = cursor.description 
		LisCorreos = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]

		correo_envio=''
		for p in LisCorreos:
			if correo_envio=='':
				correo_envio=p['correo']+';'
			else:
				correo_envio=correo_envio+p['correo']+';'

		sql_diseno=DVersionesDiseno.objects.get(pk=version_diseno_id)

		contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
		contenido = contenido + "Estimado usuario(a),<br /><br /> Env&iacute;o para su informaci&oacute;n, en el Proyecto <strong>"+sql_diseno.diseno.nombre+"</strong> de la version <strong>"+sql_diseno.nombre+"</strong> del departamento <strong>"+sql_diseno.diseno.municipio.departamento.nombre+"</strong> del municipio <strong>"+sql_diseno.diseno.municipio.nombre+"</strong> ";		
		contenido = contenido + "de la campa&ntildea <strong>"+sql_diseno.diseno.campana.nombre+"</strong>, se ha reportado la siguiente insconsistencia por el usuario <strong>"+usuario+"</strong> de la empresa <strong>"+empresa+"</strong>:'<br />'<br />" + comentario;
		contenido = contenido + '<br /><br /><br />Favor no responder este correo, es de uso informativo unicamente.<br /><br /><br />Gracias,<br /><br /><br />'
		contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'

		mail = Mensaje(
					remitente=settings.REMITENTE,
					destinatario=correo_envio,
					asunto='Notificacion de Insconsistencia en Proyecto de Gestion',
					contenido=contenido,
					appLabel='gestion de Proyecto'
					)	

		mail.simpleSend()

	except Exception as e:
		print(e)