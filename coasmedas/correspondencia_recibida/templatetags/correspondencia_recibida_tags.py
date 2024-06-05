from django import template
from correspondencia_recibida.models import CorrespondenciaRecibida,  CorrespondenciaRecibidaAsignada
from usuario.models import Usuario
from django.contrib.auth.models import Permission, User
from django.db.models import Q

from django.db.models import Max

register = template.Library()

@register.inclusion_tag('correspondencia_recibida/_miscorrespondencias.html', takes_context=True)
def miscorrespondencias(context,usr):
	if not usr or not type(usr).__name__ == 'str':
		return None  

	items=[]
	padresId=[]
	excluye=[]
	#inicio = Opcion.objects.filter(id=1)

	permisos = [(x.id) for x in Permission.objects.filter(user=usr.id)]

	usuarioActual = usr.usuario.id
	empresaId = usr.usuario.empresa.id

	# lista = [] 
	# # SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA
	# queryHistorial = CorrespondenciaRecibidaAsignada.objects.filter(correspondenciaRecibida__empresa = empresaId  ).values('correspondenciaRecibida_id').annotate(id=Max('id'))

	# # for i in queryHistorial:
	# # 	lista.append(i['id'])
	# # 	print i
	# 	# print i['id']			
	# #SE CONSULTA TODAS LAS CARTAS RECIBIDAS DE LA EMPRESA Y AL USUARIO QUE SE LE ASIGNO
	# queryset = CorrespondenciaRecibidaAsignada.objects.filter(
	# 	id__in = [answer['id'] for answer in queryHistorial]
	#  , 	usuario = usuarioActual , copia = False , estado_id__in = [33,36]).order_by('-pk')[:3]

	queryset = CorrespondenciaRecibidaAsignada.objects.raw("""
					select top 3 asignacion.id,corre.asunto, corre.radicado, asignacion.fechaAsignacion
						FROM [dbo].[correspondencia_recibida_correspondenciarecibidaasignada] asignacion
						INNER JOIN [dbo].[correspondencia_recibida_correspondenciarecibida] corre ON corre.id = asignacion.  correspondenciaRecibida_id
						where 
							asignacion.usuario_id = """+str(usuarioActual)+""" and
							asignacion.copia = 0 and asignacion.estado_id in (33,36) and
							asignacion.id in  
								(select MAX(a.id) as id
									from [dbo].[correspondencia_recibida_correspondenciarecibidaasignada] a
									INNER JOIN [dbo].[correspondencia_recibida_correspondenciarecibida] cr on cr.id = a.correspondenciaRecibida_id
									where cr.empresa_id = """+str(empresaId)+""" 
									GROUP BY a.correspondenciaRecibida_id , cr.asunto) 
						order by asignacion.id ASC""")

	queryset2 = CorrespondenciaRecibidaAsignada.objects.raw("""
					select  asignacion.id,corre.asunto, corre.radicado, asignacion.fechaAsignacion
						FROM [dbo].[correspondencia_recibida_correspondenciarecibidaasignada] asignacion
						INNER JOIN [dbo].[correspondencia_recibida_correspondenciarecibida] corre ON corre.id = asignacion.  correspondenciaRecibida_id
						where 
							asignacion.usuario_id = """+str(usuarioActual)+""" and
							asignacion.copia = 0 and asignacion.estado_id in (33,36) and
							asignacion.id in  
								(select MAX(a.id) as id
									from [dbo].[correspondencia_recibida_correspondenciarecibidaasignada] a
									INNER JOIN [dbo].[correspondencia_recibida_correspondenciarecibida] cr on cr.id = a.correspondenciaRecibida_id
									where cr.empresa_id = """+str(empresaId)+""" 
									GROUP BY a.correspondenciaRecibida_id , cr.asunto) 
						order by asignacion.id desc""")


	lista = []
	for obj in queryset:
		lista.append({ 'id': obj.id 
			, 'asunto': obj.asunto 
			,'radicado':obj.radicado 
			,'fechaAsignacion':obj.fechaAsignacion  }) 	
	
	return {'lista' : list(lista), 'ruta':context['request'].path , 'total' : len(list(queryset2)) }