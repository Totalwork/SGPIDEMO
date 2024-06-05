from django import template
# from correspondencia_recibida.models import CorrespondenciaRecibida,  CorrespondenciaRecibidaAsignada
# from usuario.models import Usuario
from parametrizacion.models import Funcionario
# from django.contrib.auth.models import Permission, User
# from django.db.models import Q

# from django.db.models import Max

register = template.Library()

@register.inclusion_tag('responsabilidades/_responsabilidades.html', takes_context=True)
def misResponsabilidades(context,usr):

	funcionario_model = Funcionario.objects.filter(persona_id = usr.usuario.persona.id, empresa=usr.usuario.empresa.id)

	if funcionario_model.exists():
		# return {'lista' : list(funcionario_model), 'ruta':context['request'].path , 'total' : funcionario_model.responsabilidades.count()}
		return {'lista' : funcionario_model[0].responsabilidades.all(), 'ruta':context['request'].path , 'total' : funcionario_model[0].responsabilidades.count()}
	else:
		return {'lista' : '', 'ruta':context['request'].path , 'total' : 0}