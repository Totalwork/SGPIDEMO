from coasmedas.celery import app
from django.db import connection
from .models import CIntervaloCronograma,BCronograma,Porcentaje,AReglasEstado,Linea,DActividad,Meta
from adminMail.models import Mensaje
from django.conf import settings
from usuario.models import Persona
from proyecto.models import Proyecto
from datetime import datetime, timedelta,date
from django.db.models import Q,Sum
import uuid
import xlsxwriter
import os
from contrato.enumeration import tipoC
from tipo.models import Tipo
from estado.models import Estado


@app.task
def updateActividad(esquema_id,actividad_id):

	cronogramas=BCronograma.objects.filter(esquema_id=esquema_id)

	for item in cronogramas:
		consulta_actividad=DActividad.objects.filter(cronograma_id=item.id,esquema_actividades_id=actividad_id)

		if len(consulta_actividad) == 0:

			actividad=DActividad(cronograma_id=item.id,esquema_actividades_id=actividad_id)
			actividad.save()

			meta=Meta(actividad_id=actividad.id,cantidad=0)
			meta.save()

			intervalos=CIntervaloCronograma.objects.filter(cronograma_id=item.id,tipo_linea=1)

			for item2 in intervalos:
				linea=Linea(tipo_linea=1,cantidad=0,actividad_id=actividad.id,intervalo_id=item2.id)
				linea.save()


			intervalos=CIntervaloCronograma.objects.filter(cronograma_id=item.id,tipo_linea=2)

			for item2 in intervalos:
				linea=Linea(tipo_linea=2,cantidad=0,actividad_id=actividad.id,intervalo_id=item2.id)
				linea.save()

			intervalos=CIntervaloCronograma.objects.filter(cronograma_id=item.id,tipo_linea=3)

			for item2 in intervalos:
				linea=Linea(tipo_linea=3,cantidad=0,actividad_id=actividad.id,intervalo_id=item2.id)
				linea.save()


@app.task
def createAsyncLine(cronograma_id,tipo_linea):

	cursor = connection.cursor()
	cursor.callproc('[avance_de_obra].[crear_linea]',[cronograma_id,tipo_linea,])


@app.task
def createAsyncIntervalo(cronograma_id,valor_intervalo):

	for x in range(1,int(valor_intervalo)+1):
		intervalo=CIntervaloCronograma(cronograma_id=cronograma_id,intervalo=x,tipo_linea=1)
		intervalo.save()

		intervalo=CIntervaloCronograma(cronograma_id=cronograma_id,intervalo=x,tipo_linea=2)
		intervalo.save()

		intervalo=CIntervaloCronograma(cronograma_id=cronograma_id,intervalo=x,tipo_linea=3)
		intervalo.save()

@app.task
def createAsyncEsquema(tipo,id_esquema,id_cronograma,id_esquema_otro):

	cursor = connection.cursor()
	if tipo==1:
		cursor.callproc('[avance_de_obra].[creacion_esquema]',[tipo,id_cronograma,id_esquema,id_esquema_otro,])
		
	else:
		if id_esquema!=id_esquema_otro:
			cursor.callproc('[avance_de_obra].[creacion_esquema]',[tipo,id_cronograma,id_esquema,id_esquema_otro,])

@app.task
def createAsyncEstado(id_cronograma,id_esquema):

	intervalo=CIntervaloCronograma.objects.filter(cronograma_id=id_cronograma,tipo_linea=3).values('id').order_by('intervalo').last()
	
	if intervalo is not None:
		porcentaje=Porcentaje.objects.filter(intervalo_id=intervalo['id'],tipo_linea=3).values('porcentaje').first()

		if porcentaje is not None:
			esquema=AReglasEstado.objects.filter(esquema_id=id_esquema).order_by('orden')

			for item in esquema:
				if item.operador==1:
					if item.limite==porcentaje['porcentaje']:
						cronograma=BCronograma.objects.get(pk=id_cronograma)
						cronograma.estado_id=item.id
						cronograma.save()
				elif item.operador==2:
					if porcentaje['porcentaje']<=item.limite:
						cronograma=BCronograma.objects.get(pk=id_cronograma)
						cronograma.estado_id=item.id
						cronograma.save()
						break
					else:
						cronograma=BCronograma.objects.get(pk=id_cronograma)
						cronograma.estado_id=None
						cronograma.save()


@app.task
def updateAsyncEstado(id_esquema):

	cronogramas=BCronograma.objects.filter(esquema_id=id_esquema)

	for item in cronogramas:

		intervalo=CIntervaloCronograma.objects.filter(cronograma_id=item.id,tipo_linea=3).values('id').order_by('intervalo').last()
		porcentaje=Porcentaje.objects.filter(intervalo_id=intervalo['id'],tipo_linea=3).values('porcentaje').first()

		esquema=AReglasEstado.objects.filter(esquema_id=id_esquema).order_by('orden')

		for item2 in esquema:
			if item2.operador==1:
				if item2.limite==porcentaje['porcentaje']:
					cronograma=BCronograma.objects.get(pk=item.id)
					cronograma.estado_id=item2.id
					cronograma.save()
			elif item2.operador==2:
				if porcentaje['porcentaje']<=item2.limite:
					cronograma=BCronograma.objects.get(pk=item.id)
					cronograma.estado_id=item2.id
					cronograma.save()
					break
				else:
					cronograma=BCronograma.objects.get(pk=item.id)
					cronograma.estado_id=None
					cronograma.save()

@app.task
def envioCorreoAvance():
	try:
		ruta = settings.STATICFILES_DIRS[0]
		rutaPapelera = ruta + '\papelera'
		cursor = connection.cursor()
		cursor.callproc('[dbo].[seguridad_social_personas_notificar]',[37,])
		columns = cursor.description 
		LisCorreos = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]

		correo_envio=''
		for p in LisCorreos:
			correo_envio=p['correo']

			proyectos=Proyecto.objects.filter(funcionario__id=p['funcionario_id'])		
			fecha = date.today() - timedelta(days=1)



			contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
			contenido = contenido + "Estimado usuario(a),<br /><br /> Adjunto env&iacute;o para su informaci&oacute;n, la relaci&oacute;n de avance de obra no actualizada. Cualquier duda por favor comun&iacute;quese con la interventor&iacute;a correspondiente."		
			contenido = contenido + '<br /><br /><br />Favor no responder este correo, es de uso informativo unicamente.<br /><br /><br />Gracias,<br /><br /><br />'
			contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'


			unique_filename = uuid.uuid4()
			nombre_archivo = '{}/{}.xlsx'.format(rutaPapelera, unique_filename)				
			workbook = xlsxwriter.Workbook(nombre_archivo)
			worksheet = workbook.add_worksheet('Todos')
			format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
			format1.set_align('center')
			format1.set_align('vcenter')
			format2=workbook.add_format({'border':0})
			format3=workbook.add_format({'border':0,'font_size':12})
			format5=workbook.add_format()
			format6=workbook.add_format()
			format5.set_num_format('yyyy-mm-dd')
			format6.set_num_format('hh:mm')
		
			worksheet.set_column('A:AF', 30)

			worksheet.set_column('A:AF', 30)
			m=[]
			worksheetarray=[]
			rowarray=[]
		
			row=1
			col=0
			valor=0

			worksheet.write('A1', 'Macrocontrato', format1)
			worksheet.write('B1', 'Contrato', format1)
			worksheet.write('C1', 'Proyecto', format1)
			worksheet.write('D1', 'Cronograma', format1)

			sw_contrato=0
			tipo_contrato=Tipo.objects.filter(codigo=8,app='contrato')
			estado_vigente=Estado.objects.filter(codigo=28,app='contrato')
			estado_porVencer=Estado.objects.filter(codigo=31,app='contrato')

			for item in proyectos:
				sw_contrato=0

				for item_contrato in item.contrato.all():
					if int(item_contrato.tipo_contrato_id)== int(tipo_contrato[0].id):
						if int(item_contrato.estado_id)==int(estado_vigente[0].id) or int(item_contrato.estado_id)==int(estado_porVencer[0].id):
							sw_contrato=1

				if sw_contrato==1:
					cronogramas=BCronograma.objects.filter(proyecto_id=item.id)

					if len(cronogramas)>0:
						for item2 in cronogramas:
							intervalos=CIntervaloCronograma.objects.filter(tipo_linea=3,cronograma_id=item2.id,sinAvance=False).order_by('intervalo')
							ultimo_intervalo=CIntervaloCronograma.objects.filter(tipo_linea=3,cronograma_id=item2.id,sinAvance=False).order_by('intervalo').last()

							intervalo_id=0
							for item3 in intervalos:
								fecha_intervalo=intervalo_fecha(item2.fecha_inicio_cronograma,item3.intervalo,item2.periodicidad.numero_dias)
								
								if str(fecha_intervalo)<=str(fecha):
									intervalo_id=item3.id
								else:
									break
							
							
							model_procentaje=Porcentaje.objects.filter(tipo_linea=3,intervalo_id=ultimo_intervalo.id).last()

							if model_procentaje.porcentaje<100:
								model_cant=Linea.objects.filter(intervalo_id=intervalo_id,tipo_linea=3).aggregate(Sum('cantidad'))
								model_cant['cantidad__sum']=0 if model_cant['cantidad__sum']==None else model_cant['cantidad__sum']

								if model_cant['cantidad__sum']==0:
									valor=valor+1
									worksheet.write(row,col, item.mcontrato.nombre,format2)
									contratos=''
									for contrato in item.contrato.exclude(tipo_contrato=tipoC.m_contrato):
										contratos = contrato.nombre+','+contratos

									worksheet.write(row,col+1, contratos,format2)
									worksheet.write(row,col+2, item.nombre,format2)
									worksheet.write(row,col+3, item2.nombre,format2)

									row +=1			
		
			if valor>0:
				workbook.close()
				mail = Mensaje(
						remitente=settings.REMITENTE,
						destinatario=correo_envio,
						asunto='Correo Avance de Obra',
						contenido=contenido,
						appLabel='avance de obra',
						tieneAdjunto=True,
						adjunto=nombre_archivo,
						copia=''
						)												
				mail.Send()
				if os.path.exists(nombre_archivo):
					os.remove(nombre_archivo)

		#mail.simpleSend()

	except Exception as e:
		print(e)

	finally:
		cursor.close()


def intervalo_fecha(fecha,intervalo,numeros_dias):

	valor=(numeros_dias*intervalo)-numeros_dias
	date1 = datetime.strptime(str(fecha), "%Y-%m-%d")
	fecha_modificada = date1 + timedelta(days=valor)
	fecha_final=datetime.strftime(fecha_modificada, "%Y-%m-%d")

	return fecha_final







