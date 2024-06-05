from rest_framework.decorators import api_view
from rest_framework.response import Response
from .function_task import FunctionTask

@api_view(['POST',])
def TrabajoEnAlturaPorVencer(request):
	try:
		FunctionTask.TrabajoEnAlturaPorVencer()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)

@api_view(['POST',])
def TrabajoEnAlturaVencido(request):
	try:
		FunctionTask.TrabajoEnAlturaVencido()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)		

@api_view(['POST',])
def SeguridadSocialVencida(request):
	try:
		FunctionTask.SeguridadSocialVencida()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)			

@api_view(['POST',])
def LicenciaPorVencer(request):
	try:
		FunctionTask.LicenciaPorVencer()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)


@api_view(['POST',])
def LicenciaVencida(request):
	try:
		FunctionTask.LicenciaVencida()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)
