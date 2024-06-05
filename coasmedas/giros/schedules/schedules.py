from rest_framework.decorators import api_view
from rest_framework.response import Response
from .function_task import FunctionTask

@api_view(['POST',])
def envioCorreoGiroPorContabilizar(request):
	try:
		FunctionTask.envioCorreoGiroPorContabilizar()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)

@api_view(['POST',])
def envioCorreoGiroPorContabilizarProcesar(request):
	try:
		FunctionTask.envioCorreoGiroPorContabilizarProcesar()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)		

@api_view(['POST',])
def envioCorreoOrdenPagoProcesar(request):
	try:
		FunctionTask.envioCorreoOrdenPagoProcesar()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)			
