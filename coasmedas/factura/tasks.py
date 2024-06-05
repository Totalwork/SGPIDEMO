
from sinin4.celery import app
from .schedules.function_task import FunctionTask

@app.task
def facturasSinContabilizar():
	try:
		FunctionTask.facturasSinContabilizar()
	except Exception as e:
		print (e)
