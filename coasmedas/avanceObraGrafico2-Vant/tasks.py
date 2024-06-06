from coasmedas.celery import app
from django.db import connection
from .models import Cronograma,CReglasEstadoG,FDetallePresupuesto,HNodo,JCantidadesNodo
from datetime import datetime, timedelta,date
from django.db.models import Q,Sum
from logs.models import Logs,Acciones


# @app.task
# def createAsyncEstado(id_cronograma):

# 	listado_porcentaje=LPorcentaje.objects.filter(tipo_linea=3,cronograma_id=id_cronograma).values('fecha').annotate(porcentaje=Sum('porcentaje')).distinct()
				
# 	porcentaje=0
# 	for item in listado_porcentaje:
# 		porcentaje=porcentaje+float(item['porcentaje'])


# 	if listado_porcentaje is not None:
# 		cronograma=Cronograma.objects.get(pk=id_cronograma)
# 		esquema=CReglasEstadoG.objects.filter(esquema_id=cronograma.presupuesto.esquema_id).order_by('orden')

# 		for item in esquema:
# 			if item.operador==1:
# 				if item.limite==porcentaje:
# 						cronograma.estado_id=item.id
# 						cronograma.save()
# 				elif item.operador==2:
# 					if porcentaje<=item.limite:
# 						cronograma.estado_id=item.id
# 						cronograma.save()
# 						break
# 					else:
# 						cronograma.estado_id=None
# 						cronograma.save()


@app.task
def updateAsyncEstado(id_esquema):

	cronogramas=Cronograma.objects.filter(esquema_id=id_esquema)

	for item in cronogramas:

		#listado_porcentaje=LPorcentaje.objects.filter(tipo_linea=3,cronograma_id=item.id).values('fecha').annotate(porcentaje=Sum('porcentaje')).distinct()
				
		porcentaje=0
		# for item3 in listado_porcentaje:
		# 	porcentaje=porcentaje+float(item3['porcentaje'])

		esquema=CReglasEstadoG.objects.filter(esquema_id=id_esquema).order_by('orden')

		for item2 in esquema:
			if item2.operador==1:
				if item2.limite==porcentaje:
					cronograma=Cronograma.objects.get(pk=item.id)
					cronograma.estado_id=item2.id
					cronograma.save()
			elif item2.operador==2:
				if porcentaje<=item2.limite:
					cronograma=Cronograma.objects.get(pk=item.id)
					cronograma.estado_id=item2.id
					cronograma.save()
					break
				else:
					cronograma=Cronograma.objects.get(pk=item.id)
					cronograma.estado_id=None
					cronograma.save()



@app.task
def agregarSinPoste(presupuesto_id,usuario_id,nodo_id):

	detallepresupuesto=FDetallePresupuesto.objects.filter(presupuesto_id=presupuesto_id)

	for item in detallepresupuesto:
		nodo=JCantidadesNodo(detallepresupuesto_id=item.id,nodo_id=nodo_id,cantidad=0)
		nodo.save()
		logs_model=Logs(usuario_id=usuario_id,accion=Acciones.accion_crear,nombre_modelo='avance_de_obra_grafico2.cantidad_nodo',id_manipulado=nodo.id)
		logs_model.save()
