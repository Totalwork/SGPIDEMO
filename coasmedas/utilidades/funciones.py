from datetime import *
import os
from django.conf import settings
import boto 
from boto.s3.key import Key
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
import uuid
from django.utils.deconstruct import deconstructible
import sys,os
#from adminMail.models import Mensaje
#from adminMail.tasks import sendAsyncMail
from logs_errors.models import Excepciones

class funciones:	
	@staticmethod
	def getMonthName(month):
		if month == 1:
			return "Enero"
		elif month == 2:
			return "Febrero"
		elif month == 3:
			return "Marzo"
		elif month == 4:
			return "Abril"
		elif month == 5:
			return "Mayo"
		elif month == 6:
			return "Junio"
		elif month == 7:
			return "Julio"
		elif month == 8:
			return "Agosto"
		elif month == 9:
			return "Septiembre"
		elif month == 10:
			return "Octubre"
		elif month == 11:
			return "Noviembre"
		elif month == 12:
			return "Diciembre"
		else:
			return "Error"

	@staticmethod
	def path_and_rename(path,prefix):
		def wrapper(instance, filename):			
			filename, file_extension = os.path.splitext(filename)			
			# get filename
			fecha=datetime.now()
			filename = '{}_{}{}{}{}{}{}{}'.format(prefix,fecha.year,fecha.month,fecha.day,fecha.hour,fecha.minute,fecha.second, file_extension)		

			return os.path.join(path, filename)
		return wrapper

	@staticmethod
	def toLog(e,modulo):
		ahora=datetime.now()
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		exepciones = Excepciones();
		message = str(e)
		exepciones.error = ('\n'+ str(ahora) + '--> ' + str(fname) +' linea ' + str(exc_tb.tb_lineno) + ' --> ' + modulo + ': ' + message)
		exepciones.modulo = modulo
		exepciones.save()
		# 		+ ' --> ' + modulo + ': ' + e.message
		# with open(settings.LOG_ERROR,'a') as f:
		# 	f.write ('\n'+ str(ahora) + '--> ' + str(fname) +' linea ' + str(exc_tb.tb_lineno) 
		# 		+ ' --> ' + modulo + ': ' + e.message)
		# 	f.close()	

	@staticmethod
	def getDeatilLog(e, modulo):
		ahora=datetime.now()
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		return str(ahora) + '--> ' + str(fname) +' linea ' + str(exc_tb.tb_lineno) + ' --> ' + modulo + ': ' + e.message

	# @staticmethod	
	# def enviar_error(mensaje, request):	
	# 	#inicio del codigo del envio de correo
	# 	contenido = '<h3>SININ - Sistema Integral de informacion</h3>'
	# 	contenido = contenido + 'Le informamos que ha ocurrido un error en el sistema SININ, a continuacion el detalle:<br><br>'	
	# 	contenido = contenido + '<b>Excepcion</b>:' + mensaje + '<br/><br/>'
	# 	contenido = contenido + '<b>Origen</b>: http://{}{}<br><br/>'.format(request.META.get('HTTP_HOST'), request.META.get('PATH_INFO'))				
	# 	contenido = contenido + '<b>Datos</b>: {}<br><br><br/>'.format(str(request.DATA))
		
	# 	contenido = contenido + 'No responder este mensaje, este correo es de uso informativo exclusivamente,<br/><br/>'
	# 	contenido = contenido + 'Soporte SININ<br/>soporte@sinin.co'
	# 	mail = Mensaje(
	# 		remitente=settings.REMITENTE,
	# 		destinatario='dacosta@totalwork.co;cvisbal0724@gmail.com',
	# 		asunto='Error SININ {}'.format(request.META.get('HTTP_HOST')),
	# 		contenido=contenido,
	# 		appLabel='Api Usuario',
	# 		)			
	# 	mail.save()
	# 	res=sendAsyncMail(mail)	
		
	@staticmethod
	def descargarArchivoS3(ruta_relativa, ruta_descarga, nombre_archivo=None):
			conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)	
			bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)	
			key = bucket.get_key(settings.MEDIAFILES_LOCATION+'/'+ruta_relativa)
			filename=os.path.basename(key.key)	
			print (key.key)
			key.get_contents_to_filename(ruta_descarga + (nombre_archivo if nombre_archivo else filename))
			key.set_contents_from_filename(ruta_descarga + (nombre_archivo if nombre_archivo else filename))



	@staticmethod
	def eliminarArchivoS3(nombre_archivo):
		conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)
		bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
		key = bucket.get_key(settings.MEDIAFILES_LOCATION+'/'+nombre_archivo)
		if key:
			key.delete()
			

	@staticmethod
	def exportarArchivoS3(ruta_relativa):
			conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)	
			bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)	
			key = bucket.get_key(settings.MEDIAFILES_LOCATION+'/'+ruta_relativa)
			print (os.path.basename(key.key))
			filename=os.path.basename(key.key)
			
			response_headers = {
		    'response-content-type': 'application/force-download',
		    'response-content-disposition':'attachment;filename="%s"'%filename
		    }
			url = key.generate_url(
						60, 
						'GET',				
						response_headers=response_headers,
		 				force_http=True)

			return HttpResponseRedirect(url)

	@staticmethod		
	def erroresSerializer(errores):
		mensaje=""					
		for x in errores:
			if mensaje == "":
				mensaje = mensaje + x + ": " + errores[x][0] if x!="non_field_errors" else mensaje + errores[x][0]
			else:
				mensaje = mensaje +"<br>"+ x + ': ' + errores[x][0] if x!="non_field_errors" else mensaje + errores[x][0]
		return mensaje	

	@staticmethod
	def toLogText(e,modulo):
		ahora=datetime.now()		
		exepciones = Excepciones()
		message = str(e)
		exepciones.error = ('\n'+ str(ahora) + '--> ' + ' linea ' + ' --> ' + modulo + ': ' + message)
		exepciones.modulo = modulo
		exepciones.save()


@deconstructible
class RandomFileName(object):
	def __init__(self, path):
		self.path = os.path.join(path, "%s%s")

	def __call__(self, _, filename):		
		extension = os.path.splitext(filename)[1]
		# fecha=datetime.now()
		# filename = '{}_{}{}{}{}{}{}'.format(fecha.year,fecha.month,fecha.day,fecha.hour,fecha.minute,fecha.second)		
		return self.path % (uuid.uuid4(), extension)
