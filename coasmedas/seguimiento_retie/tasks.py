from sinin4.celery import app
from schedules.function_task import FunctionTask

#correo enviado todos los dias a las 6am
@app.task
def EnviarCorreoVisitasNoProgramadas():
	try:
		FunctionTask.EnviarCorreoVisitasNoProgramadas();
	except Exception as e:
		print(e)
	
@app.task
def GuardarVisitasRetie():
	try:
		FunctionTask.GuardarVisitasRetie()	
	except Exception as e:
		print(e)

	