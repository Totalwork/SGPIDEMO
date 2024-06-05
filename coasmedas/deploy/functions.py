import os
from django.conf import settings

class functions():
	
	@staticmethod
	def path_and_rename(path):
		def wrapper(instance, filename):			
			filename, file_extension = os.path.splitext(filename)			
			# get filename			
			filename = '{}/{}{}'.format(instance.sistema_version.version,filename, file_extension)

			return os.path.join(path, filename)
		return wrapper