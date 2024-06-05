from sinin4.celery import app

from django.db import connection
from django.db.models import Q
from django.http import HttpResponse
from django.conf import settings

from factura.models import Factura
from financiero.models import FinancieroCuenta
from django.http import HttpResponse,JsonResponse

from parametrizacion.models import Notificacion, Funcionario
from adminMail.models import Mensaje
from sinin4.functions import functions

import xlsxwriter
import uuid
import os

from datetime import *
import calendar
from factura.enumeration import estadoFactura, notificacion

def seguimientoTestTask(request):
	try:
		notificacion_test_op()
		return JsonResponse({'message':'No se encontraron registro','success':'ok',
				'data':''})
	except Exception as e:
		raise e

@app.task
def notificacion_test_op():
	try:
		cadenaConcepto = ''
		formato_fecha = "%Y-%m-%d"
		hoy = date.today()
		hoy = datetime.strptime(str(hoy), formato_fecha)
		contenido = ''
		correo_envio = ''
		id_empresa = 4
		orden_pago= 1
		bloqueo_factura= 0
		pagada= 0
		recursos_propios= 0

		qset_test_op = (Q(estado_id = estadoFactura.activa))
		qset_test_op = qset_test_op & (Q(fecha__gte = '2018-10-31') )
		qset_test_op = qset_test_op & (Q(contrato__empresacontrato__empresa = id_empresa) )
		qset_test_op = qset_test_op & (Q(recursos_propios = recursos_propios) )
		qset_test_op = qset_test_op & (Q(orden_pago = orden_pago) )
		qset_test_op = qset_test_op & (Q(bloqueo_factura = bloqueo_factura) )
		qset_test_op = qset_test_op & (Q(pagada = pagada) )
		qset_test_op = qset_test_op & (Q(codigo_op_id__isnull = True) )

		queryset = Factura.objects.filter(qset_test_op).exclude(referencia__exact = '').exclude(referencia__exact = '0')
		noti = Funcionario.objects.filter(notificaciones=notificacion.sinTestOp, activo=1)

		if noti:
			
			for n in noti:
				# print("notif:: ", n.persona.correo)
				correo_envio = correo_envio+n.persona.correo+';'
			print (queryset.count())
			if queryset:

				unique_filename = uuid.uuid4()
				nombre_archivo = '{}.xlsx'.format(unique_filename)
				workbook = xlsxwriter.Workbook(nombre_archivo)
				worksheet = workbook.add_worksheet('TEST OP')

				format1=workbook.add_format({'border':0,'font_size':12,'bold':True})
				format1.set_align('center')
				format1.set_align('vcenter')
				format2=workbook.add_format({'border':0})
				format5=workbook.add_format()
				format5.set_num_format('yyyy-mm-dd')
				format_money=workbook.add_format({'border':False,'font_size':11,'bold':False,'valign':'vright','num_format': '$#,##0'})

				worksheet.set_column('A:A', 17)
				worksheet.set_column('B:B', 15)
				worksheet.set_column('C:C', 15)
				worksheet.set_column('D:D', 15)
				worksheet.set_column('E:E', 15)
				worksheet.set_column('F:F', 45)
				worksheet.set_column('G:G', 15)
				worksheet.set_column('H:H', 15)
				worksheet.set_column('I:I', 15)
				# format_date=workbook.add_format({'num_format': 'yyyy-mm-dd'})

				row=1
				col=0
				worksheet.write('A1', 'Radicado', format1)
				worksheet.write('B1', 'Numero Contrato', format1)
				worksheet.write('C1', 'Numero Factura', format1)
				worksheet.write('D1', 'Fecha', format1)
				worksheet.write('E1', 'Referencia', format1)
				worksheet.write('F1', 'Conceptos', format1)

				worksheet.write('G1', 'Nit', format1)
				worksheet.write('H1', 'Cod. Acreedor', format1)
				worksheet.write('I1', 'Nombre Acreedor', format1)

				worksheet.write('J1', 'Valor Factura Antes de Impuestos y Retenciones', format1)

				for fac in queryset:
					meses = ''
					fecha = ''
					# obtener numero de dias sin contabilizar
					fecha = datetime.strptime(str(fac.fecha), formato_fecha)
					diferencias = hoy - fecha
					# if diferencias.days > 9:

					worksheet.write(row, col, str(fac.radicado) ,format2)
					worksheet.write(row, col+1,fac.contrato.numero,format2)
					worksheet.write(row, col+2,fac.numero,format2)
					worksheet.write(row, col+3,str(fac.fecha),format5)
					worksheet.write(row, col+4,fac.referencia,format2)
					cadenaConcepto = fac.concepto
					# print unicode(cadenaConcepto, 'utf-8')
					# print fac.concepto
					worksheet.write(row, col+5,cadenaConcepto,format5)
					worksheet.write(row, col+6,str(fac.contrato.contratista.nit) ,format2)
					worksheet.write(row, col+7, str(fac.contrato.contratista.codigo_acreedor) ,format2)
					worksheet.write(row, col+8, fac.contrato.contratista.nombre,format2)
					#worksheet.write(row, col+8, ' ',format2)

					worksheet.write(row, col+9,fac.valor_factura,format_money)
					row +=1

				workbook.close()
				# FIN - Crear el Excel

				contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
				contenido+='Estimado usuario(a), <br/><br/>nos permitimos comunicarle que las siguientes facturas no tienen codigo <strong>TEST-OP</strong>:<br/><br/>'
				contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
				contenido+='Gracias,<br/><br/><br/>'
				contenido+='Equipo SININ<br/>'
				contenido+=settings.EMAIL_HOST_USER+'<br/>'
				contenido+='<a href="'+settings.SERVER_URL2+'/usuario/">SININ</a><br/>'
				# print nombre_archivo
				# print correo_envio
				mail = Mensaje(
					remitente=settings.REMITENTE,
					destinatario=correo_envio,
					asunto='Facturas sin codigo TEST - OP ',
					contenido=contenido,
					appLabel='factura',
					tieneAdjunto=True,
					adjunto=nombre_archivo,
					copia=''
				)
				mail.Send()
				if os.path.exists(nombre_archivo):
					os.remove(nombre_archivo)

	except Exception as e:
		print(e)
		print ('cadena q genera el error:')
		print (cadenaConcepto)

@app.task
def notificacion_codigo_compensacion():
	try:
		cadenaConcepto = ''
		correo_envio = ''
		contenido = ''
		formato_fecha = "%Y-%m-%d"
		hoy = date.today()
		hoy = datetime.strptime(str(hoy), formato_fecha)
		# estados = []
		# estados.append(estadoFactura.activa)
		# estados.append(estadoFactura.compensada)

		id_empresa = 4
		orden_pago= 1
		bloqueo_factura= 0
		pagada= 0
		recursos_propios= 1

		qset_test_op = (Q(estado_id = estadoFactura.activa))
		qset_test_op = qset_test_op & (Q(fecha__gte = '2018-10-31') )
		qset_test_op = qset_test_op & (Q(contrato__empresacontrato__empresa = id_empresa) )
		qset_test_op = qset_test_op & (Q(recursos_propios = recursos_propios) )
		qset_test_op = qset_test_op & (Q(orden_pago = orden_pago) )
		qset_test_op = qset_test_op & (Q(bloqueo_factura = bloqueo_factura) )
		qset_test_op = qset_test_op & (Q(pagada = pagada) )
		qset_test_op = qset_test_op & (Q(codigo_op_id__isnull = True) )

		queryset = Factura.objects.filter(qset_test_op).exclude(referencia__exact = '').exclude(referencia__exact = '0')

		noti = Funcionario.objects.filter(notificaciones=notificacion.sinCodigoCompensacion, activo=1)

		if noti:

			for n in noti:
				# print("notif:: ", n.persona.correo)
				correo_envio = correo_envio+n.persona.correo+';'

			if queryset:

				# INICIO - Crear el Excel
				unique_filename = uuid.uuid4()
				nombre_archivo = '{}.xlsx'.format(unique_filename)    
				workbook = xlsxwriter.Workbook(nombre_archivo)
				worksheet = workbook.add_worksheet('Facturas')

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
				worksheet.write('A1', 'Radicado', format1)
				worksheet.write('B1', 'Numero Contrato', format1)
				worksheet.write('C1', 'Numero Factura', format1)
				worksheet.write('D1', 'Fecha', format1)
				worksheet.write('E1', 'Referencia', format1)
				worksheet.write('F1', 'Conceptos', format1)

				worksheet.write('G1', 'Nit', format1)
				worksheet.write('H1', 'Cod. Acreedor', format1)
				worksheet.write('I1', 'Nombre Acreedor', format1)

				worksheet.write('J1', 'Valor Factura Antes de Impuestos y Retenciones', format1)

				for fac in queryset:
					meses = ''
					fecha = ''
					# obtener numero de dias sin contabilizar
					fecha = datetime.strptime(str(fac.fecha), formato_fecha)
					diferencias = hoy - fecha
					# if diferencias.days > 9:

					worksheet.write(row, col, str(fac.radicado) ,format2)
					worksheet.write(row, col+1,fac.contrato.numero,format2)
					worksheet.write(row, col+2,fac.numero,format2)
					worksheet.write(row, col+3,str(fac.fecha),format5)
					worksheet.write(row, col+4,fac.referencia,format2)
					cadenaConcepto = fac.concepto
					# print unicode(cadenaConcepto, 'utf-8')
					# print fac.concepto
					worksheet.write(row, col+5,cadenaConcepto,format5)
					worksheet.write(row, col+6,str(fac.contrato.contratista.nit) ,format2)
					worksheet.write(row, col+7, str(fac.contrato.contratista.codigo_acreedor) ,format2)
					worksheet.write(row, col+8, fac.contrato.contratista.nombre,format2)
					#worksheet.write(row, col+8, ' ',format2)

					worksheet.write(row, col+9,fac.valor_factura,format_money)
					row +=1

				workbook.close()
				# FIN - Crear el Excel

				contenido+='<div style="background-color: #34353F; height:40px;"><h3><p style="Color:#FFFFFF;"><strong>SININ </strong>- <b>S</b>istema <b>In</b>tegral de <b>In</b>formacion</p></h3></div><br/><br/>'
				contenido+='Estimado usuario(a), <br/><br/>nos permitimos comunicarle que las siguientes facturas no tienen codigo de <strong>compensacion</strong>:<br/><br/>'
				contenido+='Favor no responder este correo, es de uso informativo unicamente.<br/><br/>'
				contenido+='Gracias,<br/><br/><br/>'
				contenido+='Equipo SININ<br/>'
				contenido+=settings.EMAIL_HOST_USER+'<br/>'
				contenido+='<a href="'+settings.SERVER_URL2+'/usuario/">SININ</a><br/>'
				# print nombre_archivo
				# print correo_envio
				mail = Mensaje(
					remitente=settings.REMITENTE,
					destinatario=correo_envio,
					asunto='Facturas sin codigo de compensacion',
					contenido=contenido,
					appLabel='factura',
					tieneAdjunto=True,
					adjunto=nombre_archivo,
					copia=''
				)
				mail.Send()
				if os.path.exists(nombre_archivo):
					os.remove(nombre_archivo)

	except Exception as e:
		print(e)
		print ('cadena q genera el error:')
		print (cadenaConcepto)


@app.task
def updateFacturasOrdenPago():
	try:
		correo_envio = ''
		contenido = ''
		formato_fecha = "%Y-%m-%d"
		hoy = date.today()
		hoy = datetime.strptime(str(hoy), formato_fecha)
		# estados = []
		# estados.append(estadoFactura.activa)
		# estados.append(estadoFactura.compensada)

		qset = (Q(estado_id = estadoFactura.activa))
		fecha_actual = datetime.now().strftime('%Y-%m-%d')
		qset = qset &(Q(fecha_vencimiento__lt = fecha_actual))
		qset = qset & (Q(pagada = False))
		qset = qset & (Q(fecha__gte = '2018-10-31') )

		queryset = Factura.objects.filter(qset).exclude(referencia__exact = '').exclude(referencia__exact = '0').update(orden_pago = True)

	except Exception as e:
		print(e)
		print ('cadena q genera el error:')
