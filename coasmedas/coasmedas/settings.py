
#import environ
import os
import pyodbc
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

#env = environ.Env(
    # set casting, default value
    #DEBUG=(bool, False)
#)

#environ.Env.read_env(os.path.join(BASE_DIR, os.environ.get('env', '.env')))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY =  'w4-_)v9lz2fke7z!$*##fmrf8z@s#97pqo6ydme+h17xz9gfvm'

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = env('DEBUG')
DEBUG = True


TEMPLATE_DEBUG = True

#ALLOWED_HOSTS = os.environ['ALLOW_HOST'].split(',')
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'),)

# Application definition

INSTALLED_APPS = (
    # 'material.admin',
    # 'material.admin.default',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'smart_selects',
    'djcelery',
    'reportlab',   
    'rest_framework',
    'corsheaders',
    'simple_history',
    'oauth2_provider',
    'tipo',
    'estado',
    'empresa',
    'usuario', 
    'parametrizacion',
    'giros',
    'logs',
    'contrato',
    #'cuenta',
    'opcion',
    'proyecto',
    'financiero',
    'administrador_fotos',
    'ubicacion',
    'avance_de_obra',
    'seguridad_social',
    'descargo',
    'correspondencia',
    'correspondencia_recibida',
    'mi_nube',
    'poliza',
    'adminMail',
    'proceso',
    'puntos_gps',
    'factura',
    'seguimiento_retie',
    'administrador_tarea',
    'multa',
    'gestion_proyecto',
    'informe',
    'solicitud_giro',
    'seguimiento_factura',
    'deploy',
    'informe_ministerio',
    'solicitud',
    'control_cambios',
    'solicitudservicio',
    'colorfield',
    'avanceObraGrafico',
    'bitacora',
    'no_conformidad',
    'p_p_construccion',
    'logs_errors',
    'indicadorCalidad',
    'avanceObraGrafico2',
    'informe_mme',
    'cesion_economica',
    'cesion_v2', 
    'servidumbre',
    'balance_scorecard',
    'acta_reunion',
    'activos',
    'cronogramacontrato',
    'avanceObraLite',
    'whitenoise.runserver_nostatic',
)

import djcelery
djcelery.setup_loader()

MIDDLEWARE = (
   'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
)

CORS_ORIGIN_ALLOW_ALL = True

FILE_UPLOAD_HANDLERS = [
"django.core.files.uploadhandler.MemoryFileUploadHandler",
"django.core.files.uploadhandler.TemporaryFileUploadHandler",
]

ROOT_URLCONF = 'coasmedas.urls'

WSGI_APPLICATION = 'coasmedas.wsgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'sgpi_caribemar_pruebas',
        'USER': 'sa',
        'PASSWORD': 'conectaBD',
        'HOST': 'localhost\\SQLEXPRESS',
        'PORT': '',

        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes;'
        },
    },
}



#DATABASES = {
#     'default': {
#         'ENGINE': 'sql_server.pyodbc',
#         'NAME': 'sgpi_caribemar_pruebas',
#         'USER': 'sa',
#         'PASSWORD': 'conectaBD',
#         'HOST': 'localhost\\SQLEXPRESS',
#         'PORT': '',

#         'OPTIONS': {
#             'driver': 'ODBC Driver 18 for SQL Server',
#             'extra_params': 'TrustServerCertificate=yes;'
#         },
#     },
# }



# set this to False if you want to turn off pyodbc's connection pooling
DATABASE_CONNECTION_POOLING = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                # 'django.core.context_processors.request',
            ],
        },
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_L10N = True

USE_TZ = True

import dj_database_url
#db_from_env = dj_database_url.config(conn_max_age=500)
#DATABASES['default'].update(db_from_env)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'# 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# STATICFILES_STORAGE = 'coasmedas.storage.WhiteNoiseStaticFilesStorage'

MEDIA_ROOT = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2] + ['media'])
# MEDIA_URL = '/media/'

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope', 'groups': 'Access to your groups'},
    # 'OAUTH2_BACKEND_CLASS': 'oauth2_provider.oauth2_backends.JSONOAuthLibCore'
    # 'ACCESS_TOKEN_EXPIRE_SECONDS': (100 * 525600) # 86400, # 24h (It is better to choose shorter periods)
    'ACCESS_TOKEN_EXPIRE_SECONDS': (2592000 * 12 * 10) # 10 años
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ), 
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ),
    'PAGE_SIZE': 20, 
    'DEFAULT_PAGINATION_CLASS': 'utilidades.pagination.CustomPagination',   
     #'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),   
    # 'DEFAULT_AUTHENTICATION_CLASSES': (
    #     'rest_framework_oauth.authentication.OAuth2Authentication',
    # ),

}

#AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
#AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
#AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
#AWS_S3_CUSTOM_DOMAIN = '%s.s3-accelerate.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
#AWS_DEFAULT_ACL = "private"

#MEDIAFILES_LOCATION = 'media'
#MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'
LOGIN_URL = '/usuario/login/'


#configuracion para envio de correos
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'notificacionessinin@sinin.co'
EMAIL_HOST_PASSWORD = 'notificacionessinin102018'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_FROM = 'notificacionessinin@sinin.co'
SERVER = 'localhost'
REMITENTE = 'Notificaciones Sinin'
PORT_SERVER = ''
SERVER_URL = 'http://34.215.232.32'

#zona horaria de celery
CELERY_TIMEZONE ='America/Bogota'
CELERY_SEND_EVENTS=True
CELERY_RESULT_BACKEND=None
CELERYBEAT_SCHEDULER="djcelery.schedulers.DatabaseScheduler"
CELERY_ALWAYS_EAGER=False
CELERY_BROKER_URL='redis://localhost:6379/0'

LOG_ERROR = BASE_DIR + '\\logError.txt'

# reCaptcha
RECAPTCHA_PRIVATE_KEY = '6LdV0VsUAAAAACsGVLtHMxq6jSj0TfO-LednMnSr'
RECAPTCHA_PUBLIC_KEY = '6LdV0VsUAAAAANkj34li3XxSXe42_aWKm-JexvaZ'
SOURCE = 'SININ CARIBE MAR'


#tareas programadas
from celery.schedules import crontab
CELERYBEAT_SCHEDULE ={
   
    
}

MATERIAL_ADMIN_SITE = {
    'HEADER':  'Administración SININ',  # Admin site header
    'TITLE':  'SININ',  # Admin site title
    # 'FAVICON':  'path/to/favicon',  # Admin site favicon (path to static should be specified)
    'MAIN_BG_COLOR':  '#139cbb',  # Admin site main color, css color should be specified
    'MAIN_HOVER_COLOR':  '#81d0e2',  # Admin site main hover color, css color should be specified
    'PROFILE_PICTURE':  '/images/default_avatar_male.jpg',  # Admin site profile picture (path to static should be specified)
    # 'PROFILE_BG':  'path/to/image',  # Admin site profile background (path to static should be specified)
    'LOGIN_LOGO':  '/assets/img/logo.png',  # Admin site logo on login page (path to static should be specified)
    # 'LOGOUT_BG':  'path/to/image',  # Admin site background on login/logout pages (path to static should be specified)
    'SHOW_THEMES':  True,  #  Show default admin themes button
    'TRAY_REVERSE': True,  # Hide object-tools and additional-submit-line by default
    'NAVBAR_REVERSE': False,  # Hide side navbar by default
    'SHOW_COUNTS': True, # Show instances counts for each model
    'APP_ICONS': {  # Set icons for applications(lowercase), including 3rd party apps, {'application_name': 'material_icon_name', ...}
        'sites': 'send',
    },
    'MODEL_ICONS': {  # Set icons for models(lowercase), including 3rd party models, {'model_name': 'material_icon_name', ...}
        'site': 'contact_mail',
    }
}

#JQUERY_URL = True
USE_DJANGO_JQUERY = True

CADENAPROCESOINICIAL=1
PROCESOINICIAL = 2
ITEMINICIAL = 1
CADENAPRINCIPAL = 1

NUMEROCONTRATO = '4117000182'
COSTOREDMT=22775790
COSTOREDBT=2125063
COSTOTRAFO=2467089

#SERVER_URL2=os.environ['SERVER_URL2']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'error.log'),  # Ruta al archivo de registro de errores
        },
         "console": {
            "class": "logging.StreamHandler",
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "ERROR",
    },
}

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#         },
#     },
#     "root": {
#         "handlers": ["console"],
#         "level": "ERROR",
#     },
# }