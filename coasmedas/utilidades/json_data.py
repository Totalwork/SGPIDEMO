from rest_framework import serializers
import json

class JSONSerializerField(serializers.Field):
	""" Serializer for JSONField -- required to make field writable"""
	def to_internal_value(self, data):
		return json.dumps(data)
	def to_representation(self, value):
		return json.loads(value)


