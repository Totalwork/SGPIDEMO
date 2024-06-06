lista =[
'levantamiento/nodo_foto/1000202-DSC02389.jpg',
'levantamiento/nodo_foto/1000202-DSC02390.jpg',
'levantamiento/nodo_foto/1000202-DSC02391.jpg',
'levantamiento/nodo_foto/1000202-DSC02392.jpg',
'levantamiento/nodo_foto/1000202-DSC02393.jpg',
'levantamiento/nodo_foto/1000202-DSC02394.jpg',
'levantamiento/nodo_foto/1000190-DSC02494.jpg',
'levantamiento/nodo_foto/1000190-DSC02495.jpg',
'levantamiento/nodo_foto/1000190-DSC02496.jpg',
'levantamiento/nodo_foto/1000190-DSC02497.jpg',
'levantamiento/nodo_foto/1000191-DSC02491.jpg',
'levantamiento/nodo_foto/1000191-DSC02492.jpg',
'levantamiento/nodo_foto/1000191-DSC02493.jpg',
'levantamiento/nodo_foto/1000192-DSC02486.jpg',
'levantamiento/nodo_foto/1000192-DSC02487.jpg',
'levantamiento/nodo_foto/1000192-DSC02488.jpg',
'levantamiento/nodo_foto/1000192-DSC02489.jpg',
'levantamiento/nodo_foto/1000192-DSC02490.jpg',
'levantamiento/nodo_foto/1000216-DSC02196.jpg',
'levantamiento/nodo_foto/1000216-DSC02197.jpg',
'levantamiento/nodo_foto/1000216-DSC02198.jpg',
'levantamiento/nodo_foto/1000216-DSC02199.jpg',
'levantamiento/nodo_foto/1000205-DSC02277.jpg',
'levantamiento/nodo_foto/1000205-DSC02278.jpg',
'levantamiento/nodo_foto/1000206-DSC02274.jpg',
'levantamiento/nodo_foto/1000206-DSC02275.jpg',
'levantamiento/nodo_foto/1000206-DSC02276.jpg',
'levantamiento/nodo_foto/1000207-DSC02268.jpg',
'levantamiento/nodo_foto/1000207-DSC02269.jpg',
'levantamiento/nodo_foto/1000207-DSC02270.jpg',
'levantamiento/nodo_foto/1000207-DSC02271.jpg',
'levantamiento/nodo_foto/1000207-DSC02272.jpg',
'levantamiento/nodo_foto/1000207-DSC02273.jpg',
'levantamiento/nodo_foto/1000221-DSC01985.jpg',
'levantamiento/nodo_foto/1000221-DSC01986.jpg',
'levantamiento/nodo_foto/1000221-DSC01987.jpg',
'levantamiento/nodo_foto/1000222-DSC01988.jpg',
'levantamiento/nodo_foto/1000222-DSC01989.jpg',
'levantamiento/nodo_foto/1000222-DSC01991.jpg',
'levantamiento/nodo_foto/1000199-DSC02452.jpg',
'levantamiento/nodo_foto/1000199-DSC02453.jpg',
'levantamiento/nodo_foto/1000199-DSC02454.jpg',
'levantamiento/nodo_foto/1000199-DSC02455.jpg',
'levantamiento/nodo_foto/1000199-DSC02456.jpg',
'levantamiento/nodo_foto/1000200-DSC02450.jpg',
'levantamiento/nodo_foto/1000200-DSC02451.jpg',
'levantamiento/nodo_foto/1000201-DSC02441.jpg',
'levantamiento/nodo_foto/1000201-DSC02442.jpg',
'levantamiento/nodo_foto/1000201-DSC02443.jpg',
'levantamiento/nodo_foto/1000201-DSC02444.jpg',
'levantamiento/nodo_foto/1000201-DSC02445.jpg',
'levantamiento/nodo_foto/1000201-DSC02446.jpg',
'levantamiento/nodo_foto/1000201-DSC02447.jpg',
'levantamiento/nodo_foto/1000201-DSC02448.jpg',
'levantamiento/nodo_foto/1000201-DSC02449.jpg',
'levantamiento/nodo_foto/1000225-DSC01899.jpg',
'levantamiento/nodo_foto/1000226-DSC01898.jpg',
'levantamiento/nodo_foto/1000227-DSC01841.jpg',
'levantamiento/nodo_foto/1000227-DSC01842.jpg',
'levantamiento/nodo_foto/1000227-DSC01843.jpg',
'levantamiento/nodo_foto/1000227-DSC01844.jpg',
'levantamiento/nodo_foto/1000227-DSC01845.jpg',
'levantamiento/nodo_foto/1000227-DSC01846.jpg',
'levantamiento/nodo_foto/1000227-DSC01847.jpg'
]

from coasmedas.functions import functions
from datetime import date, datetime
from django.conf import settings
import os
def borrar():	
	ahora=datetime.now()
	archivo=str(ahora.year)+str(ahora.month)+str(ahora.day)+str(ahora.hour)+str(ahora.minute)+str(ahora.second)
	ruta = '{0}\\estructuras\\{1}'.format(settings.STATICFILES_DIRS[0], 'logArchivosBorrados-' + archivo)
	os.mkdir(ruta)
	file = open("{0}\\logs.txt".format(ruta), "w")
	for x in lista:	
		try:
			functions.eliminarArchivoS3(x)
		except Exception as e:			
			file.write("El archivo no se pudo borrar del S3: {0}{1}".format(x, os.linesep))
		
	return 'Archivos borrados'