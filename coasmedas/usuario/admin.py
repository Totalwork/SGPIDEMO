from django.contrib import admin
from usuario.models import Usuario, Persona
# Register your models here.

class AdminUsuario(admin.ModelAdmin):
	list_display=('user','nombres','apellidos','empresa','correo','foto_usuario')
	list_filter=('empresa',)
	search_fields=('persona__nombres','persona__apellidos','persona__correo',)	

class AdminPersona(admin.ModelAdmin):
	list_display=('nombres','apellidos','cedula','correo','telefono')
	search_fields=('nombres','apellidos','correo',)	

admin.site.register(Usuario,AdminUsuario)
admin.site.register(Persona,AdminPersona)