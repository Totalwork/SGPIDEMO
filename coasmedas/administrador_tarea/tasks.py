from sinin4.celery import app
from django.db import connection
from .models import DTareaAsignacion,TareaActividad,DTarea
from usuario.models import Usuario
from adminMail.models import Mensaje
from django.conf import settings
from datetime import *
from .enumeration import EstadoT

from sinin4.functions import functions

@app.task
def envioNotificacionPunto(lista_usuarios,id_asignacion_tarea):
	try:
		listado=Usuario.objects.filter(id__in=lista_usuarios)
		tarea=DTareaAsignacion.objects.get(pk=id_asignacion_tarea)

		correo_envio=''
		for p in listado:
			correo_envio=correo_envio+p.persona.correo+';'

		contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
		contenido = contenido + "Estimado usuario(a),<br /><br /> Env&iacute;o para su informaci&oacute;n, la relaci&oacute;n de la tarea actualizada. La tarea <strong>"+tarea.tarea.asunto+"</strong> ha sido actualizada al estado <strong>"+tarea.estado.nombre+"</strong>."		
		contenido = contenido + '<br /><br /><br />Favor no responder este correo, es de uso informativo unicamente.<br /><br /><br />Gracias,<br /><br /><br />'
		contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'

		mail = Mensaje(
					remitente=settings.REMITENTE,
					destinatario=correo_envio,
					asunto='Actualizacion de la Tarea'+' '+tarea.tarea.asunto,
					contenido=contenido,
					appLabel='administrador de tarea'
					)	

		mail.simpleSend()

	except Exception as e:
		print(e)

@app.task
def envioActividad(lista_usuarios,id_actividad):
	try:
		listado=Usuario.objects.filter(id__in=lista_usuarios)
		actividad=TareaActividad.objects.get(pk=id_actividad)

		correo_envio=''
		for p in listado:
			correo_envio=correo_envio+p.persona.correo+';'

		contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
		contenido = contenido + "Estimado usuario(a),<br /><br /> Env&iacute;o para su informaci&oacute;n, sobre <strong> "+actividad.tipo.nombre+" "+actividad.asunto+"</strong> que ha sido invitado. La actividad <strong>"+actividad.asunto+"</strong> tiene fecha para el dia <strong>"+str(actividad.fecha)+"</strong> en el lugar <strong>"+actividad.lugar+"</strong>."		
		contenido = contenido + '<br /><br /><br />Favor no responder este correo, es de uso informativo unicamente.<br /><br /><br />Gracias,<br /><br /><br />'
		contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'

		mail = Mensaje(
					remitente=settings.REMITENTE,
					destinatario=correo_envio,
					asunto='Correo '+actividad.tipo.nombre+" "+actividad.asunto,
					contenido=contenido,
					appLabel='administrador de tarea'
					)	

		mail.simpleSend()

	except Exception as e:
		print(e)

@app.task
def envioVencido():
	try:
		listado=DTarea.objects.all()
		fecha_hoy=str(datetime.now().strftime('%Y-%m-%d'))
		estado=EstadoT()	

		for item in listado:
			asignacion=DTareaAsignacion.objects.filter(tarea__id=item.id).values('estado__color','estado__icono','estado__nombre','estado__id').last()
			if asignacion[0]['estado__id']!=estado.atendida_fueraTiempo and asignacion[0]['estado__id']!=estado.atendida and asignacion[0]['estado__id']!=estado.cancelada and asignacion[0]['estado__id']!=estado.rechazada: 
				if str(fecha_hoy)>str(item.fecha_fin):
					cambio_estado=DTareaAsignacion(colaborador_id=None,tarea_id=item.id,fecha=fecha_hoy,estado_id=estado.vencida,comentario="",solicitante_id=item.usuario_responsable_id)
					cambio_estado.save()

					correo_envio=''
					if item.colaborador_actual is not None:
						correo_envio=item.colaborador_actual.usuario.persona.correo
					else:
						correo_envio=item.usuario_responsable.persona.correo

					contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
					contenido = contenido + "Estimado usuario(a),<br /><br /> Env&iacute;o para su informaci&oacute;n, sobre  la actividad <strong>"+item.asunto+"</strong> ha cambiando a estado vencido y tiene fecha <strong>"+str(item.fecha_fin)+"</strong>."		
					contenido = contenido + '<br /><br /><br />Favor no responder este correo, es de uso informativo unicamente.<br /><br /><br />Gracias,<br /><br /><br />'
					contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'

					mail = Mensaje(
								remitente=settings.REMITENTE,
								destinatario=correo_envio,
								asunto='Correo Tarea Vencida',
								contenido=contenido,
								appLabel='administrador de tarea'
								)	

					mail.simpleSend()

	except Exception as e:
		print(e)
		#functions.toLog(e,"administrador_tarea.tarea_vencida")


@app.task
def envioPorVencer():
	try:
		listado=DTarea.objects.all()
		fecha_hoy=str(datetime.now().strftime('%Y-%m-%d'))
		fecha=date.today() - timedelta(days=5)
		fecha_atras=str(fecha.strftime('%Y-%m-%d'))

		for item in listado:
			asignacion=DTareaAsignacion.objects.filter(tarea__id=item.id).values('estado__color','estado__icono','estado__nombre','estado__id').last()
			if asignacion[0]['estado__id']!=estado.atendida_fueraTiempo and asignacion[0]['estado__id']!=estado.vencida and asignacion[0]['estado__id']!=estado.atendida and asignacion[0]['estado__id']!=estado.cancelada and asignacion[0]['estado__id']!=estado.rechazada: 
				
				if str(item.fecha_fin)>str(fecha_atras):	
					cambio_estado=DTareaAsignacion(colaborador_id=None,tarea_id=item.id,fecha=fecha_hoy,estado_id=estado.por_vencer,comentario="",solicitante_id=item.usuario_responsable_id)
					cambio_estado.save()

					correo_envio=''
					if item.colaborador_actual is not None:
						correo_envio=item.colaborador_actual.usuario.persona.correo
					else:
						correo_envio=item.usuario_responsable.persona.correo

					contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
					contenido = contenido + "Estimado usuario(a),<br /><br /> Env&iacute;o para su informaci&oacute;n, sobre <strong> la actividad "+item.asunto+"</strong> ha cambiando a estado por vencer. La actividad <strong>"+item.asunto+"</strong> tiene fecha <strong>"+str(item.fecha_fin)+"</strong> 5 dias antes de vencer la tarea."		
					contenido = contenido + '<br /><br /><br />Favor no responder este correo, es de uso informativo unicamente.<br /><br /><br />Gracias,<br /><br /><br />'
					contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'

					mail = Mensaje(
								remitente=settings.REMITENTE,
								destinatario=correo_envio,
								asunto='Correo Tarea Por Vencer',
								contenido=contenido,
								appLabel='administrador de tarea'
								)	

					mail.simpleSend()

	except Exception as e:
		print(e)









