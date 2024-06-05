from django import template
from opcion.models import Opcion, Opcion_Usuario
from usuario.models import Usuario
from django.contrib.auth.models import Permission, User, Group
from django.db.models import Q

register = template.Library()

@register.inclusion_tag('opcion/_menu.html', takes_context=True)
def menu(context,usr):

	items=[]
	padresId=[]
	excluye=[]

	qset = (Q(permiso_id__in=Permission.objects.filter(user=usr.id).values('id')) |
		   Q(permiso_id__in=Permission.objects.filter(group__id__in=Group.objects.filter(user=usr.id).values('id')).values('id')) |
		   Q(permiso_id=None))
	if usr.is_superuser:
		padres = Opcion.objects.filter(padre_id=None).order_by('orden').values()
	else:
		padres = Opcion.objects.filter(qset,padre_id=None).order_by('orden').values()

	for padre in padres:
		if usr.is_superuser:
			hijos=Opcion.objects.filter(padre_id=padre['id']).order_by('orden')
		else:	
			hijos=Opcion.objects.filter(qset, padre_id=padre['id']).order_by('orden')
		if hijos.count()>0:
			padre['children']=hijos
			items.append(padre)
		else:
			if (padre['permiso_id'] is None):
				padre=None
			else:
				items.append(padre)


	return {'lista' : items, 'ruta':context['request'].path}
