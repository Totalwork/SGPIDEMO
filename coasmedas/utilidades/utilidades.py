# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import *
import os
from django.conf import settings
import boto 
from boto.s3.key import Key
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
import uuid
from django.utils.deconstruct import deconstructible
import sys,os

class Utilidades:
		
	@staticmethod
	def crearRutaTemporalArchivoS3(ruta_relativa):
		conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)	
		bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)	
		key = bucket.get_key(settings.MEDIAFILES_LOCATION+'/'+ruta_relativa)
		# print os.path.basename(key.key)
		filename= os.path.basename(key.key)
		
		# response_headers = {
		# 'response-content-type': 'application/force-download',
		# 'response-content-disposition':'attachment;filename="%s"'%filename
		# }
		url = key.generate_url(
					60, 
					'GET',				
					response_headers=None,
	 				force_http=True)

		return url# HttpResponseRedirect(url)
