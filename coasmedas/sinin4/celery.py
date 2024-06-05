# from __future__ import absolute_import

# import os

# from celery import Celery

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinin4.settings')

# from django.conf import settings

# app = Celery('CeleryApp', backend='rpc://', broker='pyamqp://')

# app.config_from_object('django.conf:settings')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# app.conf.update(
# 	BROKER_URL = 'django://',
# )

import os
from celery import Celery
from django.conf import settings

# Establecer las opciones de django para la aplicación de celery.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinin4.settings')

# Crear la aplicación de Celery
app = Celery('CeleryApp')

# Especificamos que las variables de configuración de Celery se encuentran
# en el fichero `settings.py` de Django.
# El parámetro namespace es para decir que las variables de configuración de
# Celery en el fichero settings empiezan por el prefijo *CELERY_*
app.config_from_object('django.conf:settings')

# Este método auto-registra las tareas para el broker. 
# Busca tareas dentro de todos los archivos `tasks.py` que haya en las apps
# y las envía a Redis automáticamente.
app.autodiscover_tasks(settings.INSTALLED_APPS)