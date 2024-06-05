from rest_framework.decorators import api_view
from rest_framework.response import Response
from .function_task import FunctionTask

@api_view(['POST',])
def PolizaPorVencer(request):
	try:
		FunctionTask.PolizaPorVencer()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)

@api_view(['POST',])
def PolizaVencida(request):
	try:
		FunctionTask.PolizaVencida()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)		

@api_view(['POST',])
def ActualizarEstadoPoliza(request):
	try:
		FunctionTask.ActualizarEstadoPoliza()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)			
