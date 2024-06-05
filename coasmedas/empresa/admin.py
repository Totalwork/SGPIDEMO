from django.contrib import admin

from empresa.models import Empresa, EmpresaContratante , EmpresaAcceso


# Register your models here.
class AdminEmpresa(admin.ModelAdmin):
	list_display=('nombre','nit','logo_empresa','esDisenador','esProveedor','esContratista','esContratante','abreviatura','control_pago_factura')
	list_filter=('esDisenador','esProveedor','esContratista','esContratante','abreviatura')
	search_fields=('nombre','nit',)


class AdminEmpresaAcceso(admin.ModelAdmin):
	list_display=('id','empresa','empresa_ver')
	list_filter=('empresa',)


admin.site.register(Empresa,AdminEmpresa)
admin.site.register(EmpresaAcceso,AdminEmpresaAcceso)


class AdminEmpresaContratante(admin.ModelAdmin):
	list_display=('id','empresa','empresa_ver')
	list_filter=('empresa',)
	search_fields=('empresa__nombre',)

admin.site.register(EmpresaContratante,AdminEmpresaContratante)

