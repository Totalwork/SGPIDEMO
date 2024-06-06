from coasmedas.celery import app
from .schedules.function_task import FunctionTask

@app.task
def sendMail(mail):
	return mail.Send()

@app.task
def vencimientoItems():
	try:
		FunctionTask.vencimientoItems()
	except Exception as e:
		print(e)		
