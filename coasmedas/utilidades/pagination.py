from rest_framework import pagination
from rest_framework.response import Response

class CustomPagination(pagination.PageNumberPagination):
	def get_paginated_response(self, data):		
		paginacion = {	
			'count': self.page.paginator.count,
			'per_page': self.page.paginator.per_page,
			'total_pages': self.page.paginator.num_pages,
			'current_page': self.page.number,
			'next': self.get_next_link(),
			'previous': self.get_previous_link(),
			'data': data['data']
		}
		# respuesta=Estructura.success(message, paginacion)
		#import pdb; pdb.set_trace()
		if data.get('success'):
			data['status'] = 'success' if data.get('success') == 'ok' else data.get('success')
		data['data']=paginacion	
		return Response(data)