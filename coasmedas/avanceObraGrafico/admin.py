from django.contrib import admin
from .models import APeriodicidadG, BEsquemaCapitulosG, CEsquemaCapitulosActividadesG, DReglasEstadoG, EPresupuesto
from .models import FDetallePresupuesto, GCapa, HNodo, IEnlace, JCantidadesNodo, KCronograma, LProgramacion, MEstadoCambio
from .models import NCambio, QEjecucionProgramada,LPorcentaje
# Register your models here.

class AdminAPeriodicidadG(admin.ModelAdmin):
	list_display=('nombre','numero_dias')
	search_display=('nombre',)

admin.site.register(APeriodicidadG,AdminAPeriodicidadG)

class AdminBEsquemaCapitulosG(admin.ModelAdmin):
	list_display=('macrocontrato','nombre',)
	search_display=('nombre',)
	list_filter=('macrocontrato',)

admin.site.register(BEsquemaCapitulosG,AdminBEsquemaCapitulosG)

class AdminCEsquemaCapitulosActividadesG(admin.ModelAdmin):
	list_display=('id','esquema','nivel','padre','peso',)
	search_display=('nombre',)
	list_filter=('esquema',)

admin.site.register(CEsquemaCapitulosActividadesG,AdminCEsquemaCapitulosActividadesG)

class AdminDReglasEstadoG(admin.ModelAdmin):
	list_display=('esquema','orden','operador','limite',)
	search_display=('operador',)
	list_filter=('esquema',)

admin.site.register(DReglasEstadoG,AdminDReglasEstadoG)

class AdminEPresupuesto(admin.ModelAdmin):
	list_display=('proyecto','esquema',)
	list_filter=('esquema',)

admin.site.register(EPresupuesto,AdminEPresupuesto)

class AdminFDetallePresupuesto(admin.ModelAdmin):
	list_display=('presupuesto','actividad','codigoUC','descripcionUC','valorManoObra',)
	search_display=('descripcionUC',)
	list_filter=('actividad',)

admin.site.register(FDetallePresupuesto,AdminFDetallePresupuesto)

class AdminGCapa(admin.ModelAdmin):
	list_display=('color',)
	search_display=('color',)

admin.site.register(GCapa,AdminGCapa)

class AdminHNodo(admin.ModelAdmin):
	list_display=('presupuesto','nombre','capa','longitud','latitud','noProgramado',)
	search_display=('nombre',)
	list_filter=('presupuesto',)

admin.site.register(HNodo,AdminHNodo)


class AdminIEnlace(admin.ModelAdmin):
	list_display=('nodoOrigen','nodoDestino','capa',)
	search_display=('nodoOrigen','nodoDestino',)

admin.site.register(IEnlace,AdminIEnlace)


class AdminJCantidadesNodo(admin.ModelAdmin):
	list_display=('detallepresupuesto','nodo','cantidad',)
	list_filter=('detallepresupuesto',)

admin.site.register(JCantidadesNodo,AdminJCantidadesNodo)


class AdminKCronograma(admin.ModelAdmin):
	list_display=('presupuesto','nombre','fechaInicio','estado','programacionCerrada',)
	search_display=('nombre',)
	list_filter=('presupuesto',)

admin.site.register(KCronograma,AdminKCronograma)

class AdminLProgramacion(admin.ModelAdmin):
	list_display=('cronograma','cantidadesNodo',)
	list_filter=('cronograma',)

admin.site.register(LProgramacion,AdminLProgramacion)

class AdminMEstadoCambio(admin.ModelAdmin):
	list_display=('id','nombre',)
	search_display=('nombre',)

admin.site.register(MEstadoCambio,AdminMEstadoCambio)


class AdminNCambio(admin.ModelAdmin):
	list_display=('cronograma','nombre','estado','motivo',)
	search_display=('nombre',)
	list_filter=('cronograma',)

admin.site.register(NCambio,AdminNCambio)

# class AdminPDetalleCambio(admin.ModelAdmin):
# 	list_display=('detallePresupuesto','cambio','nodo','cantidad',)
# 	list_filter=('detallePresupuesto','cambio',)

# admin.site.register(PDetalleCambio,AdminPDetalleCambio)

class AdminQEjecucionProgramada(admin.ModelAdmin):
	list_display=('programacion','cantidadEjecutada','fecha',)
	list_filter=('programacion',)

admin.site.register(QEjecucionProgramada,AdminQEjecucionProgramada)


# class AdminREjecucionCambio(admin.ModelAdmin):
# 	list_display=('detalleCambio','cantidadEjecutada','fecha',)
# 	list_filter=('detalleCambio',)

# admin.site.register(REjecucionCambio,AdminREjecucionCambio)

class AdminLPorcentaje(admin.ModelAdmin):
	list_display=('cronograma','fecha','porcentaje',)
	list_filter=('cronograma',)

admin.site.register(LPorcentaje,AdminLPorcentaje)


