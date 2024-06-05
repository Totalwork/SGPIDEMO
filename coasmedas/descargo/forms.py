from django import forms
from .models import Descargo,Correo_descargo
from estado.models import Estado
from tipo.models import Tipo
from .enumeration import estadoD
from proyecto.models import Proyecto
from contrato.models import Contrato


class DescargoForm(forms.ModelForm):
	class Meta:
		model = Descargo
		fields = ('estado','motivo_sgi','motivo_interventor',)


	def __init__(self, *args, **kwargs):
		super(DescargoForm, self).__init__(*args, **kwargs)
        # access object through self.instance...
		listEstado=Estado.objects.filter(app='descargo')
		listadonombreEstado = [(i.id, i.nombre) for i in listEstado]
		# listadonombreEstado.insert(0,[0,'Seleccione...'])
		self.fields['estado'] = forms.ChoiceField(choices=listadonombreEstado)
		self.fields['estado'].widget.attrs.update({'class' : 'form-control'})
		self.fields['estado'].widget.attrs.update({'data-bind' : 'event:{change: mostrarmotivosgi }'})
		self.fields['motivo_sgi'].widget.attrs.update({'class' : 'form-control'})
		self.fields['motivo_interventor'].widget.attrs.update({'class' : 'form-control'})
		self.fields['estado'].empty_label='Seleccione...'
		self.fields['motivo_sgi'].empty_label='Seleccione...'
		self.fields['motivo_interventor'].empty_label='Seleccione...'

	

class DescargoCorreoForm(forms.ModelForm):
	class Meta:
		model = Correo_descargo
		fields = '__all__'



	def __init__(self, *args, **kwargs):
		super(DescargoCorreoForm, self).__init__(*args, **kwargs)
        # access object through self.instance...
		listTipo=Tipo.objects.filter(app='descargo')
		listadonombretipo = [(i.id, i.nombre) for i in listTipo]
		self.fields['tipo'] = forms.ChoiceField(choices=listadonombretipo)
		self.fields['nombre'].widget.attrs.update({'class' : 'form-control'})
		self.fields['apellido'].widget.attrs.update({'class' : 'form-control'})
		self.fields['correo'].widget.attrs.update({'class' : 'form-control'})
		self.fields['tipo'].widget.attrs.update({'class' : 'form-control'})
		self.fields['contratista'].widget.attrs.update({'class' : 'form-control'})
		self.fields['contratista'].empty_label='Seleccione...'
