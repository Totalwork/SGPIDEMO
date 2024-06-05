import requests
import json
import os

class MailGun:
	
	# def __init__(self, arg):
	# 	super(MailGun, self).__init__()
	# 	self.arg = arg

	@staticmethod
	def send(subject, body, email, attachment=None):
		if attachment:
			return requests.post(
							"https://api.mailgun.net/v3/mg.sgpi.com.co/messages",
							auth=("api", os.environ['MAILGUN_KEY']),
							files=[("attachment", open(attachment))],
							data={
								"from": "SGPI|CARIBEMAR<infocaribemar@sgpi.com.co>",
								"to": [email],
								"subject": subject,
								"html": body
								# "template": data['plantilla'],
								# "h:X-Mailgun-Variables": json.dumps(data['data'])
                            })
		else:
			return requests.post(
							"https://api.mailgun.net/v3/mg.sgpi.com.co/messages",
							auth=("api", os.environ['MAILGUN_KEY']),
							data={
								"from": "SGPI|CARIBEMAR<infocaribemar@sgpi.com.co>",
								"to": [email],
								"subject": subject,
								"html": body
								# "template": data['plantilla'],
								# "h:X-Mailgun-Variables": json.dumps(data['data'])
                            })
	
	@staticmethod
	def sendMultiples(subject, body, emails, ccEmail, attachment = None):
		if attachment:
			return requests.post(
							"https://api.mailgun.net/v3/mg.sgpi.com.co/messages",
							auth=("api", os.environ['MAILGUN_KEY']),
							files=[("attachment", open(attachment))],
							data={
								"from": "SGPI|CARIBEMAR<infocaribemar@sgpi.com.co>",
								"to": emails,
								"subject": subject,
								"html": body,
								"cc": ccEmail
								# "template": data['plantilla'],
								# "h:X-Mailgun-Variables": json.dumps(data['data'])
                            })
		else:
			return requests.post(
							"https://api.mailgun.net/v3/mg.sgpi.com.co/messages",
							auth=("api", os.environ['MAILGUN_KEY']),
							data={
								"from": "SGPI|CARIBEMAR<infocaribemar@sgpi.com.co>",
								"to": emails,
								"subject": subject,
								"html": body,
								"cc": ccEmail
								# "template": data['plantilla'],
								# "h:X-Mailgun-Variables": json.dumps(data['data'])
                            })

	@staticmethod
	def sendMailgunTemplate(data):
		return requests.post(
							"https://api.mailgun.net/v3/mg.sgpi.com.co/messages",
							auth=("api", os.environ['MAILGUN_KEY']),
							data={
								"from": "SGPI|CARIBEMAR<mg@sgpi.com.co>",
								"to": data['destinatarios'],
								"subject": data['asunto'],
								"template": data['plantilla'],
								"h:X-Mailgun-Variables": json.dumps(data['data'])
								})
	
	