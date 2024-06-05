# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from sinin4.celery import app
from sinin4.functions import functions
from schedules.function_task import FunctionTask

@app.task
def TrabajoEnAlturaPorVencer():
	try:
		FunctionTask.TrabajoEnAlturaPorVencer()
	except Exception as e:
		functions.toLog(e, 'seguridad_social.task.TrabajoEnAlturaPorVencer')
		print(e)

@app.task
def TrabajoEnAlturaVencido():
	try:
		FunctionTask.TrabajoEnAlturaVencido()
	except Exception as e:
		functions.toLog(e, 'seguridad_social.task.TrabajoEnAlturaVencido')
		print(e)		

@app.task
def SeguridadSocialVencida():
	try:
		FunctionTask.SeguridadSocialVencida()
	except Exception as e:
		functions.toLog(e, 'seguridad_social.task.SeguridadSocialVencida')
		print(e)			

@app.task
def LicenciaPorVencer():
	try:
		FunctionTask.LicenciaPorVencer()
	except Exception as e:
		functions.toLog(e, 'seguridad_social.task.LicenciaPorVencer')
		print(e)


@app.task
def LicenciaVencida():
	try:
		FunctionTask.LicenciaVencida()
	except Exception as e:
		functions.toLog(e, 'seguridad_social.task.LicenciaVencida')
		print(e)	