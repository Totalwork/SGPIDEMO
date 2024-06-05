from sinin4.celery import app
from adminMail.models import Mensaje
from .models import AIndicador,BSeguimientoIndicador
from contrato.enumeration import estadoC, tipoV, notificacion
from parametrizacion.models import Funcionario
from proyecto.models import Proyecto
from contrato.models import Contrato
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Sum
from django.conf import settings
from datetime import date, datetime, timedelta

import xlsxwriter
import uuid
import os

@app.task
def sendMail(mail):
	return mail.Send()

@app.task
def NotificacionIndicadoresPorVencer():	
	correo_envio = ''
	contenido = ''
	queryset_func = Funcionario.objects.filter(notificaciones=notificacion.ic, activo=1)
	today = date.today()	
	dateNow = today.strftime("%d/%m/%Y")
	dateNow = datetime.strptime(dateNow, '%d/%m/%Y').date()
	indicador = AIndicador.objects.all()	
	IndicadoresId = []
	for i in indicador:				
		valorTotal = BSeguimientoIndicador.objects.filter(indicador_id=i.id).aggregate(Sum('valor'))
		#print valorTotal
		if (i.objetivoAnual>valorTotal['valor__sum']):
			periodicidadDias = int(i.periodicidad.dias)
			datePasada = dateNow - timedelta(days=periodicidadDias)			
			qset = (Q(indicador_id=i.id) & Q(finPeriodo__range=[datePasada,dateNow]))		
			segInidicador = BSeguimientoIndicador.objects.filter(qset)
			if not segInidicador:
				IndicadoresId.append(i)


	if IndicadoresId:
		# INICIO - Crear el Excel						
		unique_filename = uuid.uuid4()
		nombre_archivo = '{}.xlsx'.format(unique_filename)
		workbook = xlsxwriter.Workbook(nombre_archivo)
		worksheet = workbook.add_worksheet('Indicadores')
		worksheet.set_column('A:A', 40)
		worksheet.set_column('B:B', 18)
		worksheet.set_column('C:D', 12)
		worksheet.set_column('E:F', 35)
		format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
		format1.set_align('center')
		format1.set_align('vcenter')
		format2=workbook.add_format({'border':0})
		format2.set_align('center')
		format2.set_align('vcenter')
		format5=workbook.add_format()
		format5.set_num_format('yyyy-mm-dd')
		row=1
		col=0
		worksheet.write('A1', 'Nombre', format1)
		worksheet.write('B1', 'Unidad de medida', format1)
		worksheet.write('C1', 'Objetivo', format1)
		worksheet.write('D1', 'Valor Total', format1)
		worksheet.write('E1', 'Periodicidad', format1)
		
		for i in IndicadoresId:
			valorTotal = BSeguimientoIndicador.objects.filter(indicador_id=i.id).aggregate(Sum('valor'))
			worksheet.write(row, col,i.nombre,format2)
			worksheet.write(row, col+1,i.unidadMedida,format2)
			worksheet.write(row, col+2,i.objetivoAnual,format2)
			if valorTotal['valor__sum']:
				worksheet.write(row, col+3,valorTotal['valor__sum'],format2)
			else:
				worksheet.write(row, col+3,"0",format2)
			worksheet.write(row, col+4,i.periodicidad.descripcion,format2)		
			row +=1
		workbook.close()
		# FIN - Crear el Excel
		contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
		contenido+='Estimado usuario(a), <br/><br/>Nos permitimos comunicarle que los siguientes registros de indicadores de calidad no cuentan con los valores actualizados.<br/><br/>'
		contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
		contenido+='Gracias,<br/><br/><br/>'
		contenido+='Equipo SININ<br/>'
		contenido+=settings.EMAIL_HOST_USER+'<br/>'
		contenido+='<a href="'+settings.SERVER_URL2+':'+settings.PORT_SERVER+'/usuario/">SININ</a><br/>'
		
		queryset_func = Funcionario.objects.filter(notificaciones=notificacion.ic, activo=1)
		for func in queryset_func:
			correo_envio = correo_envio+func.persona.correo+';'
        #correo_envio = 'jsamper@totalwork.co;'
		if correo_envio:	            
			mail = Mensaje(
                remitente=settings.REMITENTE,
                destinatario=correo_envio,
                asunto='Indicadores de Calidad sin Avance',
                contenido=contenido,
                appLabel='indicadores',
                tieneAdjunto=True,
                adjunto=nombre_archivo,
                copia=''
			)
			mail.Send()	
			if os.path.exists(nombre_archivo):
				os.remove(nombre_archivo)	
		