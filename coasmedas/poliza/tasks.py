# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from coasmedas.celery import app
from coasmedas.functions import functions
from schedules.function_task import FunctionTask

@app.task
def PolizaPorVencer():
	try:
		FunctionTask.PolizaPorVencer()
	except Exception as e:
		functions.toLog(e, 'poliza.task.PolizaPorVencer')
		print (e)	

@app.task
def PolizaVencida():
	try:
		FunctionTask.PolizaVencida()
	except Exception as e:
		functions.toLog(e, 'poliza.task.PolizaVencida')
		print (e)				

@app.task
def ActualizarEstadoPoliza():
	try:
		FunctionTask.ActualizarEstadoPoliza()
	except Exception as e:
		functions.toLog(e, 'poliza.task.ActualizarEstadoPoliza')
		print (e)