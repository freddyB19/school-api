from django.test import TestCase
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


from apps.emails.services.send_email import ConfigEmail
from apps.emails.services.send_email import ContentHTMLMessage

class EmailsServiceSendEmailTest(TestCase):
	# assertInHTML
	# assertNotInHTML
	# assertHTMLNotEqual
	#with self.assertRaisesMessage(ValueError, "invalid literal for int()"):

	def setUp(self):
		self.email = EmailMultiAlternatives(
			"Bienvenido",
			"Saludos",
			"fredd@gmail.com",
			["calors@gmail.com"],
		)

		self.basic_email_template = render_to_string("emails/template_email_basic.html")
		
	def test_set_content_html_message(self):
		"""
			Validar que se genere el string del html del mensaje
		"""
		context = {"name": "Carlos", "password": "12345678"}

		find = f"""
		<p>
			El usuario {context['name']}, ha decidido restrablecer su contraseña
		</p>
		"""	

		reset_password_email_template = render_to_string(
			"emails/reset_user_password.html",
			context= context
		)

		content_html = ContentHTMLMessage.set_message(
			template_name = "reset_user_password.html",
			context = context
		)

		self.assertTrue(isinstance(content_html, str))
		self.assertHTMLEqual(content_html, reset_password_email_template)
		self.assertInHTML(find, content_html)
		


	def test_set_content_html_message_without_template(self):
		"""
			Validar que se genere el string del html del mensaje sin pasar el 'template' 
		"""
		context = {"name": "Carlos", "password": "12345678"}
		find = f"""
		<p>
			El usuario {context['name']}, ha decidido restrablecer su contraseña
		</p>
		"""	

		content_html = ContentHTMLMessage.set_message(
			context = context
		)

		
		self.assertTrue(isinstance(content_html, str))
		self.assertHTMLEqual(content_html, self.basic_email_template)
		self.assertNotInHTML(find, content_html)


	def test_set_content_html_message_without_nothing(self):
		"""
			Validar que se genere el string del html sin enviar nada
		"""
		content_html = ContentHTMLMessage.set_message()

		self.assertTrue(isinstance(content_html, str))
		self.assertHTMLEqual(content_html, self.basic_email_template)
