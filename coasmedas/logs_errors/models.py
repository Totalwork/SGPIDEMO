from django.db import models

# Create your models here.

class Excepciones(models.Model):
	fecha_registro = models.DateTimeField(auto_now_add=True, blank=True)
	error = models.TextField(blank=True)
	modulo = models.CharField(blank=True, max_length=100)
	class Meta:				
		permissions = (
			("can_see_excepciones","can see excepciones"),
		) 
