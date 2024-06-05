from sinin4.celery import app
from django.db import connection
from schedules.function_task import FunctionTask

@app.task
def envioCorreoGiroPorContabilizar():
	try:
		FunctionTask.envioCorreoGiroPorContabilizar()
	except Exception as e:
		print(e)

@app.task
def envioCorreoGiroPorContabilizarProcesar():
	try:
		FunctionTask.envioCorreoGiroPorContabilizarProcesar()
	except Exception as e:
		print(e)

@app.task
def envioCorreoOrdenPagoProcesar():
	try:
		FunctionTask.envioCorreoOrdenPagoProcesar()
	except Exception as e:
		print(e)
