from django.db import IntegrityError,transaction
from coasmedas.celery import app
from .models import Archivo, ArchivoUsuario
from datetime import date
import datetime
import os
from io import StringIO

@app.task
def subirArchivoAsync(archivos,empresa,usuario):

	# for e in range(1,10000):
	# 	print(e)
	insert_list = []
	sid = transaction.savepoint()
	try:
		t = datetime.datetime.now()
		contador = 1

		for line in archivos:
			# print line.name
			filename, file_extension = os.path.splitext(line.name)
			line.name = str(empresa)+'-'+str(usuario)+'-'+str(t.year)+str(t.month)+str(t.day)+str(t.hour)+str(t.minute)+str(t.second)+str(contador)+str(file_extension)
			
			archivo = Archivo.objects.filter(nombre = filename , padre = 1 , propietario_id = usuario , eliminado = 0 , tipoArchivo_id = 14 )
			if archivo.count()==0:

				insert_list.append(Archivo(nombre = filename
							,padre = 1
							,destino = line
							,tipoArchivo_id= 14
							,eliminado = 0
							,peso = 0
							,propietario_id = usuario
							,usuarioModificado_id = 1

								))
			else:
				i = 0
				contador2= 1
				while i != 1:
					archivo2 = Archivo.objects.filter(nombre = filename+' - copia'+str(contador2) , padre = 1 , propietario_id = usuario , eliminado = 0 , tipoArchivo_id = 14 )
					# print str(i)+'luis mendoza'+str(contador2)
					# print 'contador'+str(archivo2.count())
					if archivo2.count()==0:

						insert_list.append(Archivo(nombre = filename+' - copia'+str(contador2)
									,padre = 1
									,destino = line
									,tipoArchivo_id= 14
									,eliminado = 0
									,peso = 0
									,propietario_id = usuario
									,usuarioModificado_id = 1
										))
						i=1
						break
					else:

						contador2=int(contador2)+1

			contador = int(contador)+1

		Archivo.objects.bulk_create(insert_list)
		transaction.savepoint_commit(sid)
		return 29062013
	except Exception as e:
		print(e)
		# print type(e).__name__
	