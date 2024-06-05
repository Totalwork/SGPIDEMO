class Estructura:
	"""docstring for Estructura"""
	@staticmethod
	def success(message, data):
		return {'status':'success', 'message':message, 'data':data}	
	
	@staticmethod
	def error(message):
		return {'status':'error', 'message':message, 'data':None}

	@staticmethod
	def warning(message, data=None):
		return {'status':'warning', 'message':message, 'data':data}			

	@staticmethod
	def error500(e=None):
		return {'status':'error', 
				'message':'Ha ocurrido un error interno, consulte con el administrador del sistema.',
				'data':None}			
