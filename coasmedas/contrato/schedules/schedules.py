from rest_framework.decorators import api_view
from rest_framework.response import Response
from .function_task import FunctionTask

@api_view(['POST',])
def cambioEstadoContrato(request):
	try:
		FunctionTask.cambioEstadoContrato()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)

@api_view(['POST',])
def contratoDeObraPorVencidos(request):
	try:
		FunctionTask.contratoDeObraPorVencidos()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)

@api_view(['POST',])
def contratoDeObraVencidos(request):
	try:
		FunctionTask.contratoDeObraVencidos()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)

@api_view(['POST',])
def contratoAuxiliarPorVencer(request):
	try:
		FunctionTask.contratoAuxiliarPorVencer()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)

@api_view(['POST',])
def contratoAuxiliaresVencidos(request):
	try:
		FunctionTask.contratoAuxiliaresVencidos()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)
