from rest_framework.decorators import api_view
from rest_framework.response import Response
from .function_task import FunctionTask

@api_view(['POST',])
def vencimientoItems(request):
	try:
		FunctionTask.vencimientoItems()
		return Response({'message':'','success':'ok','data': None})
	except Exception as e:
		print(e)
