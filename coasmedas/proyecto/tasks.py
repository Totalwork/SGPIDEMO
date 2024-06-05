from sinin4.celery import app

from django.db import connection
from django.db.models import Q
from django.http import HttpResponse
from django.conf import settings

from proyecto.models import Proyecto

from parametrizacion.models import Notificacion, Funcionario
from adminMail.models import Mensaje
from sinin4.functions import functions

import xlsxwriter
import uuid
import os

from datetime import *
import calendar

@app.task
def notificacionProyecto(proyecto,usuario):	
	#import pdb; pdb.set_trace()
	proyecto_nombre = str(proyecto['nombre'])
	departamento_nombre = str(proyecto['municipio']['departamento']['nombre'])
	municipio_nombre = str(proyecto['municipio']['nombre'])
	fondo_nombre = str(proyecto['tipo_proyecto']['fondo_proyecto']['nombre'])
	mcontrato_nombre = str(proyecto['mcontrato']['nombre'])	
	usuario_nombre = str(usuario.persona.nombres + ' ' + usuario.persona.apellidos)
	usuario_empresa = str(usuario.empresa.nombre)


	# arrayNotiInternoTemp = ['yassera@totalwork.co']
	arrayNotiInternoTemp = ['yassera@totalwork.co','dacosta@totalwork.co','jsamper@totalwork.co']
	for func in arrayNotiInternoTemp:	
		if func:
			correo_envio = func+';'
			contenido = ''
			contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/>'
			contenido+='Se ha registrado satifactoriamente un Proyecto, se relaciona la informacion ingresada al sistema:<br/><br/>'
			contenido+='''
				<style type="text/css">
					table, td, th {  
						border: 1px solid #ddd;
						text-align: left;
					}
					table {
						border-collapse: collapse;
						width: 100%;
					}
					th, td {
						padding: 15px;
					}
				</style>
				<h3>Informacion del proyecto ingresado</h3>			
				<table>
				<thead>
				<tr>
					<th>Proyecto</th>
					<th>Contrato con el MME</th>
					<th>Departamento</th>
					<th>Municipio</th>
					<th>Fondo</th>
				</tr>
				</thead>
				<tbody>
				<tr>
					<td style="width:40%">'''+proyecto_nombre+'''</td>
					<td style="width:20%">'''+mcontrato_nombre+'''</td>
					<td style="width:20%">'''+departamento_nombre+'''</td>
					<td style="width:20%">'''+municipio_nombre+'''</td>			
					<td style="width:20%">'''+fondo_nombre+'''</td>
				</tr>
				</tbody>
				</table>	
				<br/><br/>
				<h3>Informacion del usuario que creo el proyecto</h3>
				<table>
				<thead>
				<tr>
					<th>Usuario</th>
					<th>Empresa</th>
				</tr>
				</thead>
				<tbody>
				<tr>
					<td style="width:50%">'''+usuario_nombre+'''</td>
					<td style="width:50%">'''+usuario_empresa+'''</td>
				</tr>
				</tbody>
				</table>	
				<br/><br/>
			'''
			contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
			contenido+='Gracias,<br/><br/><br/>'
			contenido+='Equipo SININ<br/>'					
			contenido+=settings.EMAIL_HOST_USER+'<br/>'
			contenido+='<a href= "'+settings.SERVER_URL2+'/usuario/">SININ</a><br/>'
			#contenido+='<a href= "https://caribesol.sinin.co/">SININ</a><br/>'
			mail = Mensaje(
				remitente=settings.REMITENTE,
				destinatario=correo_envio,
				asunto=' Nuevo Proyecto',
				contenido=contenido,
				appLabel='mcontrato',
				tieneAdjunto=False,			
				copia=''
			)

			mail.Send() 