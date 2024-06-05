import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Replace sender@example.com with your "From" address.
# This address must be verified with Amazon SES.
SENDER = "SGPI|CARIBEMAR<infocaribemar@mail.sgpi.com.co>"

# Specify a configuration set. If you do not want to use a configuration
# set, comment the following variable, and the 
# ConfigurationSetName=CONFIGURATION_SET argument below.
CONFIGURATION_SET = "sgpi-configuration"

# If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
AWS_REGION = "us-west-2"

# The character encoding for the email.
CHARSET = "UTF-8"

class Mail:

	@staticmethod
	def send(subject, body, email, attachment=None):
		
		SUBJECT = subject

		# The email body for recipients with non-HTML email clients.
		BODY_TEXT = ("No responder este mensaje")

		# The HTML body of the email.
		BODY_HTML = body

		# Create a new SES resource and specify a region.
		client = boto3.client('ses',region_name=AWS_REGION,
							aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
							aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])


		if attachment:			
			msg = MIMEMultipart('mixed')
			msg['Subject'] = SUBJECT
			msg['From'] = SENDER
			msg['To'] = email
			msg_body = MIMEMultipart('alternative')
			textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
			htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
			msg_body.attach(textpart)
			msg_body.attach(htmlpart)
			att = MIMEApplication(open(attachment, 'rb').read())
			att.add_header('Content-Disposition','attachment',filename=os.path.basename(attachment))
			msg.attach(msg_body)
			msg.attach(att)
			try:
				#Provide the contents of the email.
				response = client.send_raw_email(
					Source=SENDER,
					Destinations=[ email, ],
					RawMessage={
						'Data': msg.as_string(),
					},
					ConfigurationSetName=CONFIGURATION_SET
				)
				# Display an error if something goes wrong.
			except ClientError as e:
				print(e.response['Error']['Message'])
				return (e.response['Error']['Message'])
			else:
				print("Email sent! Message ID:")
				print(response['MessageId'])
				return (response['MessageId'])      
		else:	
		# Try to send the email.
			try:
				#Provide the contents of the email.
				
				response = client.send_email(
					Destination={
						'ToAddresses': [
							email,
						],
					},
					Message={
						'Body': {
							'Html': {
								'Charset': CHARSET,
								'Data': BODY_HTML,
							},
							'Text': {
								'Charset': CHARSET,
								'Data': BODY_TEXT,
							},
						},
						'Subject': {
							'Charset': CHARSET,
							'Data': SUBJECT,
						},
					},
					Source=SENDER,
					# If you are not using a configuration set, comment or delete the
					# following line
					ConfigurationSetName=CONFIGURATION_SET
				)
			# Display an error if something goes wrong.	
			except ClientError as e:
				return (e.response['Error']['Message'])
			else:
				return (response['MessageId'])       

	@staticmethod
	def sendTemplate(data):
		client = boto3.client('ses',region_name=AWS_REGION,
							aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID_MAIL'], # settings.AWS_ACCESS_KEY_ID,
							aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY_MAIL']) # settings.AWS_SECRET_ACCESS_KEY)
		try:

			data['data']['subject'] = data['asunto']
			
			response = client.send_templated_email(
				Destination={
					'ToAddresses': data['destinatarios']
				},
				Template=data['plantilla'],
				Source=SENDER,
				TemplateData=json.dumps(data['data'])
			)
			
			return response
		# Display an error if something goes wrong.	
		except ClientError as e:
			return (e.response['Error']['Message'])
		else:
			return (response['MessageId'])       

	@staticmethod
	def sendMultiples(subject, body, emails, ccEmail):
		

		# The subject line for the email.
		SUBJECT = subject

		# The email body for recipients with non-HTML email clients.
		BODY_TEXT = ("No responder este mensaje")

		# The HTML body of the email.
		BODY_HTML = body

		# Create a new SES resource and specify a region.
		client = boto3.client('ses',region_name=AWS_REGION,
							aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], # settings.AWS_ACCESS_KEY_ID,
							aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])  #settings.AWS_SECRET_ACCESS_KEY)

		# Try to send the email.
		try:
			#Provide the contents of the email.
			response = client.send_email(
				Destination={
					'ToAddresses': emails,
                    'CcAddresses': ccEmail
				},
				Message={
					'Body': {
						'Html': {
							'Charset': CHARSET,
							'Data': BODY_HTML,
						},
						'Text': {
							'Charset': CHARSET,
							'Data': BODY_TEXT,
						},
					},
					'Subject': {
						'Charset': CHARSET,
						'Data': SUBJECT,
					},
				},
				Source=SENDER,
				# If you are not using a configuration set, comment or delete the
				# following line
				ConfigurationSetName=CONFIGURATION_SET,
			)
		# Display an error if something goes wrong.	
		except ClientError as e:
			return (e.response['Error']['Message'])
		else:
			return (response['MessageId'])       
