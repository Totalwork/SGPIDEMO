from rest_framework.decorators import api_view
from rest_framework.response import Response
from .function_task import FunctionTask

@api_view(['POST',])
def EnviarCorreoVisitasNoProgramadas(request):
	try:
		FunctionTask.EnviarCorreoVisitasNoProgramadas()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)

@api_view(['POST',])
def GuardarVisitasRetie(request):
	try:
		FunctionTask.GuardarVisitasRetie()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)		

