from django.contrib import admin
from .models import Archivo, ArchivoUsuario 
# Register your models here.

# Register your models here.
class AdminArchivo(admin.ModelAdmin):
	list_display=( 'id' , 'nombre' , 'padre' , 'tipoArchivo' , 'peso' , 'propietario' , 'fechaModificado' , 'usuarioModificado' , 'eliminado')
	list_filter=('propietario', 'tipoArchivo' , 'eliminado')
	search_fields=('nombre',)

class AdminArchivoUsuario(admin.ModelAdmin):
	list_display=('usuario' , 'archivo' , 'escritura' )
	list_filter=('usuario', 'archivo' , 'escritura')
	search_fields=('usuario',)

admin.site.register(Archivo, AdminArchivo )
admin.site.register(ArchivoUsuario, AdminArchivoUsuario )
