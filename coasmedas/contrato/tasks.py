from coasmedas.celery import app
from coasmedas.functions import functions
from .schedules.function_task import FunctionTask

@app.task
def cambioEstadoContrato():
	try:
		FunctionTask.cambioEstadoContrato()
	except Exception as e:
		functions.toLog(e,'Tasks Cambiar Estado Contrato')

@app.task
def contratoDeObraPorVencidos():
	try:
		FunctionTask.contratoDeObraPorVencidos()
	except Exception as e:
		functions.toLog(e,'Tasks Contratos por vencer')

@app.task
def contratoDeObraVencidos():
	try:
		FunctionTask.contratoDeObraVencidos()
	except Exception as e:
		functions.toLog(e,'Tasks Contratos vencidos')

@app.task
def contratoAuxiliarPorVencer():
	try:
		FunctionTask.contratoAuxiliarPorVencer()
	except Exception as e:
		functions.toLog(e,'Tasks Contratos auxiliares por vencer')

@app.task
def contratoAuxiliaresVencidos():
	try:
		FunctionTask.contratoAuxiliaresVencidos()
	except Exception as e:
		functions.toLog(e,'Tasks Contratos auxiliares vencidos')

@app.task
def notificacionMcontrato(mcontrato,usuario):
	try:
		FunctionTask.notificacionMcontrato(mcontrato,usuario)
	except Exception as e:
		functions.toLog(e,'Tasks Contratos notificacion Mcontrato')
