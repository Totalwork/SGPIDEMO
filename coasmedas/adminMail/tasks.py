# from sinin4.celery import app
from adminMail.models import Mensaje
import os
from django.conf import settings
import shutil

# @app.task
def sendAsyncMail(mail):
	return mail.simpleSend()

# @app.task
def sendAsyncFullMail(mail):
	return mail.Send()	

# @app.task
def sendPeriodically():
	mail=Mensaje(asunto='test cada 2 minuto - CARIBE MAR',
		contenido='contenido del mensaje enviado cada 2 minutos',
		remitente='Notificaciones@sinin.co',
		destinatario='didi_acosta@hotmail.com')
	return mail.simpleSend()


# @app.task
def EliminarArchivosTemporales():

	#eliminar archivos de static
	ruta = settings.STATICFILES_DIRS[0]
	rutaPapelera = ruta + '\papelera'  
	folder_path = rutaPapelera
	if os.path.exists(folder_path):
		for file_object in os.listdir(folder_path):
			file_object_path = os.path.join(folder_path, file_object)
			if os.path.isfile(file_object_path):
				os.unlink(file_object_path)
			else:
				shutil.rmtree(file_object_path)

	#eliminar archivos de media		
	ruta_media = settings.MEDIA_ROOT
	rutaPapelera = ruta_media + '\mi_nube\descargas'  
	folder_path = rutaPapelera
	if os.path.exists(folder_path):
		for file_object in os.listdir(folder_path):
			file_object_path = os.path.join(folder_path, file_object)
			if os.path.isfile(file_object_path):
				os.unlink(file_object_path)
			else:
				shutil.rmtree(file_object_path)		

		return True	