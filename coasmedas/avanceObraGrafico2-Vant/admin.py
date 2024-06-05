from django.contrib import admin
from .models import APeriodicidadG,BEsquemaCapitulosG,CEsquemaCapitulosActividadesG,CReglasEstadoG,Cronograma,DiagramaGrahm
from .models import EPresupuesto,FDetallePresupuesto,GCapa,HNodo,IEnlace
# Register your models here.

class AdminAPeriodicidadGrafico(admin.ModelAdmin):
	list_display=('nombre','numero_dias')
	search_display=('nombre',)

admin.site.register(APeriodicidadG,AdminAPeriodicidadGrafico)


class AdminEsqsuemaCapituloGrafico(admin.ModelAdmin):
	list_display=('nombre','macrocontrato')
	search_display=('nombre',)
	list_filter=('macrocontrato',)

admin.site.register(BEsquemaCapitulosG,AdminEsqsuemaCapituloGrafico)

class AdminEsqsuemaCapituloActividadGrafico(admin.ModelAdmin):
	list_display=('nombre','esquema','nivel','padre')
	search_display=('nombre',)
	list_filter=('esquema','padre')

admin.site.register(CEsquemaCapitulosActividadesG,AdminEsqsuemaCapituloActividadGrafico)


class AdminReglaEstadoGrafico(admin.ModelAdmin):
	list_display=('nombre','esquema','orden',)
	search_display=('nombre',)
	list_filter=('esquema',)

admin.site.register(CReglasEstadoG,AdminReglaEstadoGrafico)


class AdminCronogramaGrafico(admin.ModelAdmin):
	list_display=('nombre','proyecto','estado','esquema','programacionCerrada')
	search_display=('nombre',)
	list_filter=('proyecto','estado','esquema')

admin.site.register(Cronograma,AdminCronogramaGrafico)


class AdminDiagramaGrahmGrafico(admin.ModelAdmin):
	list_display=('cronograma','actividad','fechaInicio','fechaFinal','actividad_inicial')
	search_display=('cronograma',)
	list_filter=('cronograma','actividad',)

admin.site.register(DiagramaGrahm,AdminDiagramaGrahmGrafico)

class AdminPresupuestoGrafico(admin.ModelAdmin):
	list_display=('nombre','cronograma','cerrar_presupuesto')
	search_display=('nombre',)
	list_filter=('cronograma',)

admin.site.register(EPresupuesto,AdminPresupuestoGrafico)


class AdminDetallePresupuestoGrafico(admin.ModelAdmin):
	list_display=('presupuesto','actividad','codigoUC','descripcionUC','valorGlobal','porcentaje')
	search_display=('presupuesto',)
	list_filter=('presupuesto','actividad',)

admin.site.register(FDetallePresupuesto,AdminDetallePresupuestoGrafico)


class AdminCapaGrafico(admin.ModelAdmin):
	list_display=('nombre','color')
	search_display=('nombre',)

admin.site.register(GCapa,AdminCapaGrafico)


class AdminNodoGrafico(admin.ModelAdmin):
	list_display=('presupuesto','latitud','longitud','noProgramado')
	search_display=('presupuesto',)
	list_filter=('presupuesto',)

admin.site.register(HNodo,AdminNodoGrafico)


class AdminEnlaceGrafico(admin.ModelAdmin):
	list_display=('detallepresupuesto','nodoOrigen','nodoDestino','capa')
	search_display=('detallepresupuesto',)
	list_filter=('detallepresupuesto',)

admin.site.register(IEnlace,AdminEnlaceGrafico)