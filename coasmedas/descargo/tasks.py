from sinin4.celery import app
from django.db import connection
from adminMail.models import Mensaje
from .models import Correo_descargo,AIdInternoDescargo,ATrabajo,AManiobra,ABMotivoSgi,AMotivoInterventor,Descargo,FotoDescargo
from .enumeration import notifi
from contrato.enumeration import tipoC
import uuid
import xlsxwriter
from datetime import datetime, timedelta
from django.db.models import Q
from django.conf import settings
import os
from sinin4.functions import functions
from parametrizacion.models import Funcionario
from contrato.models import EmpresaContrato
# Para Eliminar
# from django.http import JsonResponse #HttpResponse

# Notificacion Descargo para contratista
@app.task
def NotificacionDescargo():
	nombre_modulo = 'Descargo - NotificacionDescargo'
	try:
		tipo_c=tipoC()

		personas_notificar=Correo_descargo.objects.filter(tipo_id = 99)

		for p in personas_notificar:
			#if p.id == 163:

			#print p.contratista.id
			# print p.contratista.nombre

			contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
			contenido = contenido + "Estimado usuario(a),<br /><br /> Adjunto env&iacute;o para su informaci&oacute;n, la relaci&oacute;n de descargos actualizada. Cualquier duda por favor comun&iacute;quese con la interventor&iacute;a correspondiente."
			contenido = contenido + '<br /><br /><br />Favor no responder este correo, es de uso informativo unicamente.<br /><br /><br />Gracias,<br /><br /><br />'
			contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
			unique_filename = uuid.uuid4()
			ruta = settings.STATICFILES_DIRS[0]
			nombre_archivo = ruta+'\papelera\{}.xlsx'.format(unique_filename) 
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
			m=[]
			worksheetarray=[]
			rowarray=[]

			row=1
			col=0
			trabajos=''
			trs=''

			last_month = datetime.today() - timedelta(days=180)
			qset=(Q(proyecto__contrato__tipo_contrato_id=tipo_c.contratoProyecto)) & (
					Q(proyecto__contrato__contratista_id=p.contratista.id)) & (Q(fecha__gte=last_month))

			queryset = Descargo.objects.filter(qset).order_by('-id')
			descargos = []
			for des in queryset:
				verificar = esSoloLectura(des.proyecto.mcontrato, p.contratista.id)
				if verificar == False:
					descargos.append(des)

			worksheet.write('A1', 'Consultor', format1)
			worksheet.write('B1', 'ID interno', format1)
			worksheet.write('C1', 'Convenio/Contrato', format1)
			worksheet.write('D1', 'No. Descargo', format1)
			worksheet.write('E1', 'Estado Descargo', format1)
			worksheet.write('F1', 'Municipio', format1)
			worksheet.write('G1', 'Contratista', format1)
			worksheet.write('H1', 'Nombre Proyecto', format1)
			worksheet.write('I1', 'Numero Contrato', format1)
			worksheet.write('J1', 'Barrio', format1)
			worksheet.write('K1', 'Direccion', format1)
			worksheet.write('L1', 'BDI', format1)
			worksheet.write('M1', 'Orden de Servicio', format1)
			worksheet.write('N1', 'Area Afectada', format1)
			worksheet.write('O1', 'Elemento a intervenir', format1)
			worksheet.write('P1', 'Maniobra', format1)
			worksheet.write('Q1', 'Trabajo', format1)
			worksheet.write('R1', 'Fecha', format1)
			worksheet.write('S1', 'Hora inicio', format1)
			worksheet.write('T1', 'Hora fin', format1)
			worksheet.write('U1', 'Jefe trabajo', format1)
			worksheet.write('V1', 'Agente zona de trabajo', format1)
			worksheet.write('W1', 'Observacion', format1)
			worksheet.write('X1', 'Motivo SGI', format1)
			worksheet.write('Y1', 'Observacion interventoria', format1)
			worksheet.write('Z1', 'Motivo interventor', format1)
			worksheet.write('AA1', 'No. Requerimiento', format1)
			worksheet.write('AB1', 'Correo BDI', format1)
			worksheet.write('AC1', 'Formato IPDC', format1)
			worksheet.write('AD1', 'Soporte Protocolo', format1)
			worksheet.write('AE1', 'Lista de chequeo', format1)
			worksheet.write('AF1', 'Estado Registro', format1)

			if descargos:
				for descargo in descargos:

					if descargo.proyecto.municipio.departamento.id not in m:
						m.append(descargo.proyecto.municipio.departamento.id)
						worksheetarray.append(workbook.add_worksheet(str(descargo.proyecto.municipio.departamento.nombre)))
			
						posicion= m.index(descargo.proyecto.municipio.departamento.id)
			
						rowarray.append(1)
			
						worksheetarray[posicion].set_column('A:AF', 30)
			
						worksheetarray[posicion].write('A1', 'Consultor', format1)
						worksheetarray[posicion].write('B1', 'ID interno', format1)
						worksheetarray[posicion].write('C1', 'Convenio/Contrato', format1)
						worksheetarray[posicion].write('D1', 'No. Descargo', format1)
						worksheetarray[posicion].write('E1', 'Estado Descargo', format1)
						worksheetarray[posicion].write('F1', 'Municipio', format1)
						worksheetarray[posicion].write('G1', 'Contratista', format1)
						worksheetarray[posicion].write('H1', 'Nombre Proyecto', format1)
						worksheetarray[posicion].write('I1', 'Numero Contrato', format1)
						worksheetarray[posicion].write('J1', 'Barrio', format1)
						worksheetarray[posicion].write('K1', 'Direccion', format1)
						worksheetarray[posicion].write('L1', 'BDI', format1)
						worksheetarray[posicion].write('M1', 'Orden de Servicio', format1)
						worksheetarray[posicion].write('N1', 'Area Afectada', format1)
						worksheetarray[posicion].write('O1', 'Elemento a intervenir', format1)
						worksheetarray[posicion].write('P1', 'Maniobra', format1)
						worksheetarray[posicion].write('Q1', 'Trabajo', format1)
						worksheetarray[posicion].write('R1', 'Fecha', format1)
						worksheetarray[posicion].write('S1', 'Hora inicio', format1)
						worksheetarray[posicion].write('T1', 'Hora fin', format1)
						worksheetarray[posicion].write('U1', 'Jefe trabajo', format1)
						worksheetarray[posicion].write('V1', 'Agente zona de trabajo', format1)
						worksheetarray[posicion].write('W1', 'Observacion', format1)
						worksheetarray[posicion].write('X1', 'Motivo SGI', format1)
						worksheetarray[posicion].write('Y1', 'Observacion interventoria', format1)
						worksheetarray[posicion].write('Z1', 'Motivo interventor', format1)
						worksheetarray[posicion].write('AA1', 'No. Requerimiento', format1)
						worksheetarray[posicion].write('AB1', 'Correo BDI', format1)
						worksheetarray[posicion].write('AC1', 'Formato IPDC', format1)
						worksheetarray[posicion].write('AD1', 'Soporte Protocolo', format1)
						worksheetarray[posicion].write('AE1', 'Lista de chequeo', format1)
						worksheetarray[posicion].write('AF1', 'Estado Registro', format1)
			
					if descargo.proyecto.municipio.departamento.id in m:
			
			
						posicion= m.index(descargo.proyecto.municipio.departamento.id)
			
						# if detalle.cuenta is not None:
						# 	cuenta_nombre= "Girar de la cuenta de %s No. %s ' - ' %s" % (detalle.cuenta.nombre , detalle.cuenta.numero, detalle.cuenta.fiduciaria) if detalle.cuenta.nombre is not None else ''
				
						# if detalle.cuenta is not None:
						# 	cuenta_referencia= detalle.encabezado.referencia  if detalle.encabezado.referencia is not None else ''	
						#worksheet.write(row, col,descargo.nombre,format2)
						worksheetarray[posicion].write(rowarray[posicion], col+1,descargo.id_interno,format2)#id interno
						worksheetarray[posicion].write(rowarray[posicion], col+2,descargo.proyecto.mcontrato.nombre,format2)#convenio/contrato
						worksheetarray[posicion].write(rowarray[posicion], col+3,descargo.numero,format2)#No.Descargo
						worksheetarray[posicion].write(rowarray[posicion], col+4,descargo.estado.nombre,format2)#estado descargo
						worksheetarray[posicion].write(rowarray[posicion], col+5,descargo.proyecto.municipio.nombre,format2)#municipio
						worksheetarray[posicion].write(rowarray[posicion], col+6,descargo.contratista.nombre,format2)#contratista
						worksheetarray[posicion].write(rowarray[posicion], col+7,descargo.proyecto.nombre,format2)#nombre proyecto
						worksheetarray[posicion].write(rowarray[posicion], col+9,descargo.barrio,format2)#Barrio
						worksheetarray[posicion].write(rowarray[posicion], col+10,descargo.direccion,format2)#direccion
						if descargo.bdi==False:
							worksheetarray[posicion].write(rowarray[posicion], col+11,'No',format2)#BDI
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+11,'Si',format2)#BDI
						if descargo.perdida_mercado==False:
							worksheetarray[posicion].write(rowarray[posicion], col+12,'No',format2)#Orden de servicio
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+12,'Si',format2)#Orden de servicio
						worksheetarray[posicion].write(rowarray[posicion], col+13,descargo.area_afectada,format2)#Area Afectada
						worksheetarray[posicion].write(rowarray[posicion], col+14,descargo.elemento_intervenir,format2)#Elemento a intervenir
						worksheetarray[posicion].write(rowarray[posicion], col+15,descargo.maniobra.nombre,format2)#Maniobra
						for trabajo in descargo.trabajo.all():
							trabajos = trabajo.nombre+','+trabajos
						trabajos=trabajos[:-1]
						worksheetarray[posicion].write(rowarray[posicion], col+16,trabajos,format2)#Trabajo
						trabajos=''
						worksheetarray[posicion].write(rowarray[posicion], col+17,descargo.fecha,format5)#Fecha
						worksheetarray[posicion].write(rowarray[posicion], col+18,descargo.hora_inicio,format6)#Hora inicio
						worksheetarray[posicion].write(rowarray[posicion], col+19,descargo.hora_fin,format6)#hora fin
						worksheetarray[posicion].write(rowarray[posicion], col+20,descargo.jefe_trabajo.persona.nombres+' '+descargo.jefe_trabajo.persona.apellidos,format2)#Jefe trabajo
						worksheetarray[posicion].write(rowarray[posicion], col+21,descargo.agente_descargo.persona.nombres+' '+descargo.agente_descargo.persona.apellidos,format2)#Agente zona de trabajo
						worksheetarray[posicion].write(rowarray[posicion], col+22,descargo.observacion,format2)#Observacion
						if descargo.motivo_sgi==None:
							worksheetarray[posicion].write(rowarray[posicion], col+23,'',format2)#Motivo SGI
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+23,descargo.motivo_sgi.nombre,format2)#Motivo SGI
						worksheetarray[posicion].write(rowarray[posicion], col+24,descargo.observacion_interventor,format2)#Observacion interventoria
						if descargo.motivo_interventor==None:
							worksheetarray[posicion].write(rowarray[posicion], col+25,'',format2)#Motivo interventor
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+25,descargo.motivo_interventor.nombre,format2)#Motivo interventor
						worksheetarray[posicion].write(rowarray[posicion], col+26,descargo.numero_requerimiento,format2)#No requerimiento
						if descargo.correo_bdi==None:
							worksheetarray[posicion].write(rowarray[posicion], col+27,'Por Subir',format2)#Correo BDI
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+27,str(descargo.correo_bdi),format2)#Correo BDI
						if descargo.soporte_ops==None:
							worksheetarray[posicion].write(rowarray[posicion], col+28,'Por subir',format2)#Formato IPDC
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+28,str(descargo.soporte_ops),format2)#Formato IPDC
						if descargo.soporte_protocolo==None:
							worksheetarray[posicion].write(rowarray[posicion], col+29,descargo.soporte_protocolo,format2)#Soporte protocolo
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+29,str(descargo.soporte_protocolo),format2)#Soporte protocolo
						if descargo.lista_chequeo==None:
							worksheetarray[posicion].write(rowarray[posicion], col+30,'Por subir',format2)#Lista de chequeo
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+30,str(descargo.lista_chequeo),format2)#Lista de chequeo
						#worksheetarray[posicion].write(rowarray[posicion], col+12,descargo.estado.nombre,format2)#Estado Registro
				
				
						for contrato in descargo.proyecto.contrato.all():
							if contrato.tipo_contrato.id == tipoC.contratoProyecto:
								worksheetarray[posicion].write(rowarray[posicion], col+8,contrato.numero,format5)
							if contrato.tipo_contrato.id == tipoC.interventoria:
								worksheetarray[posicion].write(rowarray[posicion], col,contrato.contratista.nombre,format5)
					
						rowarray[posicion]=rowarray[posicion]+1
						#worksheet.write(row, col+7,detalle.cuenta.nombre if detalle.cuenta is not None else '',format2)
					worksheet.write(row, col+1,descargo.id_interno,format2)#id interno
					worksheet.write(row, col+2,descargo.proyecto.mcontrato.nombre,format2)#convenio/contrato
					worksheet.write(row, col+3,descargo.numero,format2)#No.Descargo
					worksheet.write(row, col+4,descargo.estado.nombre,format2)#estado descargo
					worksheet.write(row, col+5,descargo.proyecto.municipio.nombre,format2)#municipio
					worksheet.write(row, col+6,descargo.contratista.nombre,format2)#contratista
					worksheet.write(row, col+7,descargo.proyecto.nombre,format2)#nombre proyecto
					worksheet.write(row, col+9,descargo.barrio,format2)#Barrio
					worksheet.write(row, col+10,descargo.direccion,format2)#direccion
					if descargo.bdi==False:
						worksheet.write(row, col+11,'No',format2)#BDI
					else:
						worksheet.write(row, col+11,'Si',format2)#BDI
					if descargo.perdida_mercado==False:
						worksheet.write(row, col+12,'No',format2)#Orden de servicio
					else:
						worksheet.write(row, col+12,'Si',format2)#Orden de servicio
					worksheet.write(row, col+13,descargo.area_afectada,format2)#Area Afectada
					worksheet.write(row, col+14,descargo.elemento_intervenir,format2)#Elemento a intervenir
					worksheet.write(row, col+15,descargo.maniobra.nombre,format2)#Maniobra
					for tr in descargo.trabajo.all():
							trs = tr.nombre+','+trs
					trs=trs[:-1]
					worksheet.write(row, col+16,trs,format2)#Trabajo
					trs=''
					#worksheet.write(row, col+12,descargo.estado.nombre,format2)#Trabajo
					worksheet.write(row, col+17,descargo.fecha,format5)#Fecha
					worksheet.write(row, col+18,descargo.hora_inicio,format6)#Hora inicio
					worksheet.write(row, col+19,descargo.hora_fin,format6)#hora fin
					worksheet.write(row, col+20,descargo.jefe_trabajo.persona.nombres+' '+descargo.jefe_trabajo.persona.apellidos,format2)#Jefe trabajo
					worksheet.write(row, col+21,descargo.agente_descargo.persona.nombres+' '+descargo.agente_descargo.persona.apellidos,format2)#Agente zona de trabajo
					worksheet.write(row, col+22,descargo.observacion,format2)#Observacion
					if descargo.motivo_sgi==None:
						worksheet.write(row, col+23,'',format2)#Motivo SGI
					else:
						worksheet.write(row, col+23,descargo.motivo_sgi.nombre,format2)#Motivo SGI
					worksheet.write(row, col+24,descargo.observacion_interventor,format2)#Observacion interventoria
					if descargo.motivo_interventor==None:
						worksheet.write(row, col+25,'',format2)#Motivo interventor
					else:
						worksheet.write(row, col+25,descargo.motivo_interventor.nombre,format2)#Motivo interventor
					worksheet.write(row, col+26,descargo.numero_requerimiento,format2)#No requerimiento
					if descargo.correo_bdi==None:
						worksheet.write(row, col+27,'Por Subir',format2)#Correo BDI
					else:
						worksheet.write(row, col+27,str(descargo.correo_bdi),format2)#Correo BDI
					if descargo.soporte_ops==None:
						worksheet.write(row, col+28,'Por subir',format2)#Formato IPDC
					else:
						worksheet.write(row, col+28,str(descargo.soporte_ops),format2)#Formato IPDC
					if descargo.soporte_protocolo==None:
						worksheet.write(row, col+29,descargo.soporte_protocolo,format2)#Soporte protocolo
					else:
						worksheet.write(row, col+29,str(descargo.soporte_protocolo),format2)#Soporte protocolo
					if descargo.lista_chequeo==None:
						worksheet.write(row, col+30,'Por subir',format2)#Lista de chequeo
					else:
						worksheet.write(row, col+30,str(descargo.lista_chequeo),format2)#Lista de chequeo
					#worksheet.write(row, col+12,descargo.estado.nombre,format2)#Estado Registro

					for contrato in descargo.proyecto.contrato.all():
						if contrato.tipo_contrato.id == tipoC.contratoProyecto:
							worksheet.write(row, col+8,contrato.numero,format5)
						if contrato.tipo_contrato.id == tipoC.interventoria:
							worksheet.write(row, col,contrato.contratista.nombre,format5)
					
					row +=1
				# Fin del For
				workbook.close()
				mail = Mensaje(
						remitente=settings.REMITENTE,
						destinatario=p.correo,
						asunto='Correo Descargos',
						contenido=contenido,
						appLabel='descargo',
						tieneAdjunto=True,
						adjunto=nombre_archivo,
						copia=''
						)
				mail.Send()
				if os.path.exists(nombre_archivo):
					os.remove(nombre_archivo)
				#print mail.adjunto
				# print "correo: "+str(p.correo)
			# else:
			# 	print "Sin Registros"

		# return JsonResponse({'message':'Ok','success':'ok','data':''})
	except Exception as e:
		functions.toLog(e,nombre_modulo)
		#print(e)

# Notificacion Descargo para Funcionarios
@app.task
def NotificacionDescargoFuncionario():
	nombre_modulo = 'Descargo - NotificacionDescargoFuncionario'
	try:
		# tipo_c=tipoC()

		queryset_func = Funcionario.objects.filter(notificaciones=notifi.cod, activo=1)
		# correo_envio=''
		for f in queryset_func:
			#print f.persona.nombres+' '+f.persona.apellidos
			#if f.id == 224:
			# print f.persona.correo

			contenido='<h3>SININ - Sistema Integral de informaci&oacute;n</h3><br><br>'
			contenido = contenido + "Estimado usuario(a),<br /><br /> Adjunto env&iacute;o para su informaci&oacute;n, la relaci&oacute;n de descargos actualizada. Cualquier duda por favor comun&iacute;quese con la interventor&iacute;a correspondiente."	
			contenido = contenido + '<br /><br /><br />Favor no responder este correo, es de uso informativo unicamente.<br /><br /><br />Gracias,<br /><br /><br />'
			contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
			unique_filename = uuid.uuid4()
			ruta = settings.STATICFILES_DIRS[0]
			nombre_archivo = ruta+'\papelera\{}.xlsx'.format(unique_filename) 				
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
			m=[]
			worksheetarray=[]
			rowarray=[]

			row=1
			col=0
			trabajos=''
			trs=''

			last_month = datetime.today() - timedelta(days=180)

			qset=(Q(fecha__gte=last_month)) & (Q(proyecto__funcionario__id = f.id))

			queryset = Descargo.objects.filter(qset).order_by('-id')
			descargos = []
			for des in queryset:
				verificar = esSoloLectura(des.proyecto.mcontrato, p.contratista.id)
				if verificar == False:
					descargos.append(des)

			worksheet.write('A1', 'Consultor', format1)
			worksheet.write('B1', 'ID interno', format1)
			worksheet.write('C1', 'Convenio/Contrato', format1)
			worksheet.write('D1', 'No. Descargo', format1)
			worksheet.write('E1', 'Estado Descargo', format1)
			worksheet.write('F1', 'Municipio', format1)
			worksheet.write('G1', 'Contratista', format1)
			worksheet.write('H1', 'Nombre Proyecto', format1)
			worksheet.write('I1', 'Numero Contrato', format1)
			worksheet.write('J1', 'Barrio', format1)
			worksheet.write('K1', 'Direccion', format1)
			worksheet.write('L1', 'BDI', format1)
			worksheet.write('M1', 'Orden de Servicio', format1)
			worksheet.write('N1', 'Area Afectada', format1)
			worksheet.write('O1', 'Elemento a intervenir', format1)
			worksheet.write('P1', 'Maniobra', format1)
			worksheet.write('Q1', 'Trabajo', format1)
			worksheet.write('R1', 'Fecha', format1)
			worksheet.write('S1', 'Hora inicio', format1)
			worksheet.write('T1', 'Hora fin', format1)
			worksheet.write('U1', 'Jefe trabajo', format1)
			worksheet.write('V1', 'Agente zona de trabajo', format1)
			worksheet.write('W1', 'Observacion', format1)
			worksheet.write('X1', 'Motivo SGI', format1)
			worksheet.write('Y1', 'Observacion interventoria', format1)
			worksheet.write('Z1', 'Motivo interventor', format1)
			worksheet.write('AA1', 'No. Requerimiento', format1)
			worksheet.write('AB1', 'Correo BDI', format1)
			worksheet.write('AC1', 'Formato IPDC', format1)
			worksheet.write('AD1', 'Soporte Protocolo', format1)
			worksheet.write('AE1', 'Lista de chequeo', format1)
			worksheet.write('AF1', 'Estado Registro', format1)

			if descargos:
				for descargo in descargos:

					if descargo.proyecto.municipio.departamento.id not in m:
						m.append(descargo.proyecto.municipio.departamento.id)
						worksheetarray.append(workbook.add_worksheet(str(descargo.proyecto.municipio.departamento.nombre)))
			
						posicion= m.index(descargo.proyecto.municipio.departamento.id)
			
						rowarray.append(1)
			
						worksheetarray[posicion].set_column('A:AF', 30)
			
						worksheetarray[posicion].write('A1', 'Consultor', format1)
						worksheetarray[posicion].write('B1', 'ID interno', format1)
						worksheetarray[posicion].write('C1', 'Convenio/Contrato', format1)
						worksheetarray[posicion].write('D1', 'No. Descargo', format1)
						worksheetarray[posicion].write('E1', 'Estado Descargo', format1)
						worksheetarray[posicion].write('F1', 'Municipio', format1)
						worksheetarray[posicion].write('G1', 'Contratista', format1)
						worksheetarray[posicion].write('H1', 'Nombre Proyecto', format1)
						worksheetarray[posicion].write('I1', 'Numero Contrato', format1)
						worksheetarray[posicion].write('J1', 'Barrio', format1)
						worksheetarray[posicion].write('K1', 'Direccion', format1)
						worksheetarray[posicion].write('L1', 'BDI', format1)
						worksheetarray[posicion].write('M1', 'Orden de Servicio', format1)
						worksheetarray[posicion].write('N1', 'Area Afectada', format1)
						worksheetarray[posicion].write('O1', 'Elemento a intervenir', format1)
						worksheetarray[posicion].write('P1', 'Maniobra', format1)
						worksheetarray[posicion].write('Q1', 'Trabajo', format1)
						worksheetarray[posicion].write('R1', 'Fecha', format1)
						worksheetarray[posicion].write('S1', 'Hora inicio', format1)
						worksheetarray[posicion].write('T1', 'Hora fin', format1)
						worksheetarray[posicion].write('U1', 'Jefe trabajo', format1)
						worksheetarray[posicion].write('V1', 'Agente zona de trabajo', format1)
						worksheetarray[posicion].write('W1', 'Observacion', format1)
						worksheetarray[posicion].write('X1', 'Motivo SGI', format1)
						worksheetarray[posicion].write('Y1', 'Observacion interventoria', format1)
						worksheetarray[posicion].write('Z1', 'Motivo interventor', format1)
						worksheetarray[posicion].write('AA1', 'No. Requerimiento', format1)
						worksheetarray[posicion].write('AB1', 'Correo BDI', format1)
						worksheetarray[posicion].write('AC1', 'Formato IPDC', format1)
						worksheetarray[posicion].write('AD1', 'Soporte Protocolo', format1)
						worksheetarray[posicion].write('AE1', 'Lista de chequeo', format1)
						worksheetarray[posicion].write('AF1', 'Estado Registro', format1)
			
					if descargo.proyecto.municipio.departamento.id in m:
			
			
						posicion= m.index(descargo.proyecto.municipio.departamento.id)
			
						# if detalle.cuenta is not None:
						# 	cuenta_nombre= "Girar de la cuenta de %s No. %s ' - ' %s" % (detalle.cuenta.nombre , detalle.cuenta.numero, detalle.cuenta.fiduciaria) if detalle.cuenta.nombre is not None else ''
				
						# if detalle.cuenta is not None:
						# 	cuenta_referencia= detalle.encabezado.referencia  if detalle.encabezado.referencia is not None else ''	
						#worksheet.write(row, col,descargo.nombre,format2)
						worksheetarray[posicion].write(rowarray[posicion], col+1,descargo.id_interno,format2)#id interno
						worksheetarray[posicion].write(rowarray[posicion], col+2,descargo.proyecto.mcontrato.nombre,format2)#convenio/contrato
						worksheetarray[posicion].write(rowarray[posicion], col+3,descargo.numero,format2)#No.Descargo
						worksheetarray[posicion].write(rowarray[posicion], col+4,descargo.estado.nombre,format2)#estado descargo
						worksheetarray[posicion].write(rowarray[posicion], col+5,descargo.proyecto.municipio.nombre,format2)#municipio
						worksheetarray[posicion].write(rowarray[posicion], col+6,descargo.contratista.nombre,format2)#contratista
						worksheetarray[posicion].write(rowarray[posicion], col+7,descargo.proyecto.nombre,format2)#nombre proyecto
						worksheetarray[posicion].write(rowarray[posicion], col+9,descargo.barrio,format2)#Barrio
						worksheetarray[posicion].write(rowarray[posicion], col+10,descargo.direccion,format2)#direccion
						if descargo.bdi==False:
							worksheetarray[posicion].write(rowarray[posicion], col+11,'No',format2)#BDI
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+11,'Si',format2)#BDI
						if descargo.perdida_mercado==False:
							worksheetarray[posicion].write(rowarray[posicion], col+12,'No',format2)#Orden de servicio
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+12,'Si',format2)#Orden de servicio
						worksheetarray[posicion].write(rowarray[posicion], col+13,descargo.area_afectada,format2)#Area Afectada
						worksheetarray[posicion].write(rowarray[posicion], col+14,descargo.elemento_intervenir,format2)#Elemento a intervenir
						worksheetarray[posicion].write(rowarray[posicion], col+15,descargo.maniobra.nombre,format2)#Maniobra
						for trabajo in descargo.trabajo.all():
							trabajos = trabajo.nombre+','+trabajos
						trabajos=trabajos[:-1]
						worksheetarray[posicion].write(rowarray[posicion], col+16,trabajos,format2)#Trabajo
						trabajos=''
						worksheetarray[posicion].write(rowarray[posicion], col+17,descargo.fecha,format5)#Fecha
						worksheetarray[posicion].write(rowarray[posicion], col+18,descargo.hora_inicio,format6)#Hora inicio
						worksheetarray[posicion].write(rowarray[posicion], col+19,descargo.hora_fin,format6)#hora fin
						worksheetarray[posicion].write(rowarray[posicion], col+20,descargo.jefe_trabajo.persona.nombres+' '+descargo.jefe_trabajo.persona.apellidos,format2)#Jefe trabajo
						worksheetarray[posicion].write(rowarray[posicion], col+21,descargo.agente_descargo.persona.nombres+' '+descargo.agente_descargo.persona.apellidos,format2)#Agente zona de trabajo
						worksheetarray[posicion].write(rowarray[posicion], col+22,descargo.observacion,format2)#Observacion
						if descargo.motivo_sgi==None:
							worksheetarray[posicion].write(rowarray[posicion], col+23,'',format2)#Motivo SGI
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+23,descargo.motivo_sgi.nombre,format2)#Motivo SGI
						worksheetarray[posicion].write(rowarray[posicion], col+24,descargo.observacion_interventor,format2)#Observacion interventoria
						if descargo.motivo_interventor==None:
							worksheetarray[posicion].write(rowarray[posicion], col+25,'',format2)#Motivo interventor
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+25,descargo.motivo_interventor.nombre,format2)#Motivo interventor
						worksheetarray[posicion].write(rowarray[posicion], col+26,descargo.numero_requerimiento,format2)#No requerimiento
						if descargo.correo_bdi==None:
							worksheetarray[posicion].write(rowarray[posicion], col+27,'Por Subir',format2)#Correo BDI
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+27,str(descargo.correo_bdi),format2)#Correo BDI
						if descargo.soporte_ops==None:
							worksheetarray[posicion].write(rowarray[posicion], col+28,'Por subir',format2)#Formato IPDC
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+28,str(descargo.soporte_ops),format2)#Formato IPDC
						if descargo.soporte_protocolo==None:
							worksheetarray[posicion].write(rowarray[posicion], col+29,descargo.soporte_protocolo,format2)#Soporte protocolo
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+29,str(descargo.soporte_protocolo),format2)#Soporte protocolo
						if descargo.lista_chequeo==None:
							worksheetarray[posicion].write(rowarray[posicion], col+30,'Por subir',format2)#Lista de chequeo
						else:
							worksheetarray[posicion].write(rowarray[posicion], col+30,str(descargo.lista_chequeo),format2)#Lista de chequeo
						#worksheetarray[posicion].write(rowarray[posicion], col+12,descargo.estado.nombre,format2)#Estado Registro
				
				
						for contrato in descargo.proyecto.contrato.all():
							if contrato.tipo_contrato.id == tipoC.contratoProyecto:
								worksheetarray[posicion].write(rowarray[posicion], col+8,contrato.numero,format5)
							if contrato.tipo_contrato.id == tipoC.interventoria:
								worksheetarray[posicion].write(rowarray[posicion], col,contrato.contratista.nombre,format5)
					
						rowarray[posicion]=rowarray[posicion]+1
						#worksheet.write(row, col+7,detalle.cuenta.nombre if detalle.cuenta is not None else '',format2)
					worksheet.write(row, col+1,descargo.id_interno,format2)#id interno
					worksheet.write(row, col+2,descargo.proyecto.mcontrato.nombre,format2)#convenio/contrato
					worksheet.write(row, col+3,descargo.numero,format2)#No.Descargo
					worksheet.write(row, col+4,descargo.estado.nombre,format2)#estado descargo
					worksheet.write(row, col+5,descargo.proyecto.municipio.nombre,format2)#municipio
					worksheet.write(row, col+6,descargo.contratista.nombre,format2)#contratista
					worksheet.write(row, col+7,descargo.proyecto.nombre,format2)#nombre proyecto
					worksheet.write(row, col+9,descargo.barrio,format2)#Barrio
					worksheet.write(row, col+10,descargo.direccion,format2)#direccion
					if descargo.bdi==False:
						worksheet.write(row, col+11,'No',format2)#BDI
					else:
						worksheet.write(row, col+11,'Si',format2)#BDI
					if descargo.perdida_mercado==False:
						worksheet.write(row, col+12,'No',format2)#Orden de servicio
					else:
						worksheet.write(row, col+12,'Si',format2)#Orden de servicio
					worksheet.write(row, col+13,descargo.area_afectada,format2)#Area Afectada
					worksheet.write(row, col+14,descargo.elemento_intervenir,format2)#Elemento a intervenir
					worksheet.write(row, col+15,descargo.maniobra.nombre,format2)#Maniobra
					for tr in descargo.trabajo.all():
							trs = tr.nombre+','+trs
					trs=trs[:-1]
					worksheet.write(row, col+16,trs,format2)#Trabajo
					trs=''
					#worksheet.write(row, col+12,descargo.estado.nombre,format2)#Trabajo
					worksheet.write(row, col+17,descargo.fecha,format5)#Fecha
					worksheet.write(row, col+18,descargo.hora_inicio,format6)#Hora inicio
					worksheet.write(row, col+19,descargo.hora_fin,format6)#hora fin
					worksheet.write(row, col+20,descargo.jefe_trabajo.persona.nombres+' '+descargo.jefe_trabajo.persona.apellidos,format2)#Jefe trabajo
					worksheet.write(row, col+21,descargo.agente_descargo.persona.nombres+' '+descargo.agente_descargo.persona.apellidos,format2)#Agente zona de trabajo
					worksheet.write(row, col+22,descargo.observacion,format2)#Observacion
					if descargo.motivo_sgi==None:
						worksheet.write(row, col+23,'',format2)#Motivo SGI
					else:
						worksheet.write(row, col+23,descargo.motivo_sgi.nombre,format2)#Motivo SGI
					worksheet.write(row, col+24,descargo.observacion_interventor,format2)#Observacion interventoria
					if descargo.motivo_interventor==None:
						worksheet.write(row, col+25,'',format2)#Motivo interventor
					else:
						worksheet.write(row, col+25,descargo.motivo_interventor.nombre,format2)#Motivo interventor
					worksheet.write(row, col+26,descargo.numero_requerimiento,format2)#No requerimiento
					if descargo.correo_bdi==None:
						worksheet.write(row, col+27,'Por Subir',format2)#Correo BDI
					else:
						worksheet.write(row, col+27,str(descargo.correo_bdi),format2)#Correo BDI
					if descargo.soporte_ops==None:
						worksheet.write(row, col+28,'Por subir',format2)#Formato IPDC
					else:
						worksheet.write(row, col+28,str(descargo.soporte_ops),format2)#Formato IPDC
					if descargo.soporte_protocolo==None:
						worksheet.write(row, col+29,descargo.soporte_protocolo,format2)#Soporte protocolo
					else:
						worksheet.write(row, col+29,str(descargo.soporte_protocolo),format2)#Soporte protocolo
					if descargo.lista_chequeo==None:
						worksheet.write(row, col+30,'Por subir',format2)#Lista de chequeo
					else:
						worksheet.write(row, col+30,str(descargo.lista_chequeo),format2)#Lista de chequeo
					#worksheet.write(row, col+12,descargo.estado.nombre,format2)#Estado Registro

					for contrato in descargo.proyecto.contrato.all():
						if contrato.tipo_contrato.id == tipoC.contratoProyecto:
							worksheet.write(row, col+8,contrato.numero,format5)
						if contrato.tipo_contrato.id == tipoC.interventoria:
							worksheet.write(row, col,contrato.contratista.nombre,format5)
					
					row +=1
				# Fin del For
				workbook.close()
				mail = Mensaje(
						remitente=settings.REMITENTE,
						destinatario=f.persona.correo,
						asunto='Correo Descargos',
						contenido=contenido,
						appLabel='descargo',
						tieneAdjunto=True,
						adjunto=nombre_archivo,
						copia=''
						)
				mail.Send()
				if os.path.exists(nombre_archivo):
					os.remove(nombre_archivo)
				#print mail.adjunto
			# else:
			# 	print "Sin Registros"

		# return JsonResponse({'message':'Ok','success':'ok','data':''})
	except Exception as e:
		functions.toLog(e,nombre_modulo)
		#print(e)


def esSoloLectura(contratoObj, empresa):
	contrato = contratoObj.id
	
	empresaContrato = EmpresaContrato.objects.filter(contrato__id=contrato, empresa__id=empresa).first()
	soloLectura = False if empresaContrato is not None and empresaContrato.edita else True
	return soloLectura
