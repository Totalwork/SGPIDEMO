from django.conf import settings
from storages.backends import s3boto3

class MediaStorage(s3boto3.S3Boto3Storage):
	location = settings.MEDIAFILES_LOCATION