# -*- coding: utf-8 -*- 
from coasmedas.celery import app
from django.conf import settings

from datetime import *

from django.db.models import Max
from django.db import connection
import xlsxwriter
import uuid
import os

from adminMail.models import Mensaje


from correspondencia.models import CorrespondenciaEnviada , CorrespondenciaSoporte , CorrespondenciaConsecutivo 
from parametrizacion.models import Funcionario 

from correspondencia.enumeration import Notificaciones

@app.task
def correspondenciaSinSoporte():
	
	try:

		formato_fecha = "%Y-%m-%d"
		hoy = date.today()
		hoy = datetime.strptime(str(hoy), formato_fecha)

		notificacion = Notificaciones()

		funcionarios_notificar = Funcionario.objects.filter(notificaciones=notificacion.cartas_enviadas_sin_cargar_soporte ,activo=True)

		for f in funcionarios_notificar:

			try:
				empresaId = f.empresa_id

				queryset = CorrespondenciaEnviada.objects.filter(anulado = False , usuarioSolicitante__persona_id = f.persona.id)
				querySoporte = CorrespondenciaSoporte.objects.filter(anulado = 0, correspondencia_id__in = queryset).values('correspondencia_id')
				queryset = queryset.exclude(id__in = querySoporte)	

				if queryset:

					correo_envio = ''
					contenido = ''
					correo_envio = f.persona.correo
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

					worksheet.write('A1', unicode('Fecha de elaboración', 'utf-8'), format5)
					worksheet.write('B1', 'Consecutivo', format1)
					worksheet.write('C1', 'Asunto', format1)
					worksheet.write('D1', 'Referencia', format1)
					worksheet.write('E1', 'Empresa Destino', format1)

					for objecto in queryset:
						meses = ''
						fecha = ''

						worksheet.write(row, col  ,objecto.consecutivo,format2)
						worksheet.write(row, col+1,str(objecto.prefijo.nombre)+' - '+str(objecto.consecutivo),format2)
						worksheet.write(row, col+2,objecto.asunto,format2)
						worksheet.write(row, col+3,objecto.referencia,format2)
						worksheet.write(row, col+4,objecto.empresa_destino,format2)

						row +=1

					workbook.close()# FIN - Crear el Excel

					contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
					contenido+='Estimado usuario(a), <br/><br/>nos permitimos comunicarle que las siguientes correspondencias elaboradas , no tienen cargado el <strong>soporte</strong>:<br/><br/>'
					contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
					contenido+='Gracias,<br/><br/><br/>'
					contenido+='Equipo SININ<br/>'
					contenido+='soporte@sinin.co<br/>'
					contenido+='<a href="http://52.42.43.115:8000/usuario/">SININ</a><br/>'

					mail = Mensaje(
						remitente=settings.REMITENTE,
						destinatario=correo_envio,
						asunto='Correspondencia enviada sin cargar el soporte',
						contenido=contenido,
						appLabel='correspondencia',
						tieneAdjunto=True,
						adjunto=nombre_archivo,
						copia=''
					)
					mail.Send()
					if os.path.exists(nombre_archivo):
						os.remove(nombre_archivo)

			except Exception as e:
				print(e)

	except Exception as e:
		print(e)