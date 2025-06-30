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

		find = f"""{context['name'].capitalize()}"""	

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
		find = f"""{context['name'].capitalize()} """	

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

	def test_set_config_email(self):
		"""
			Validar configuraciones para un simple email
		"""
		subject = "Titulo del mensaje"
		from_email = "admin@gmail.com"
		to = ['user1@gmail.com']
		content = "Saludos"
		
		email = ConfigEmail.set_config(
			subject = subject,
			from_email = from_email,
			to = to,
			content = content
		)

		self.assertEqual(email.content_subtype, "text")
		self.assertEqual(email.subject, subject)
		self.assertEqual(email.from_email, from_email)
		self.assertEqual(email.to, to)
		self.assertEqual(email.body, content)

	def test_set_config_email_with_template_message(self):
		"""
			Validar configuraciones para email con un template como mensaje
		"""
		subject = "Titulo del mensaje"
		from_email = "admin@gmail.com"
		to = ['user1@gmail.com']
		content = ContentHTMLMessage.set_message(
			template_name = "reset_user_password.html",
			context = {"name": "Carlos", "password": "12345678"}
		)
		
		email = ConfigEmail.set_config(
			subject = subject,
			from_email = from_email,
			to = to,
			content = content,
			subtype = "html"
		)

		self.assertEqual(email.content_subtype, "html")
		self.assertEqual(email.subject, subject)
		self.assertEqual(email.from_email, from_email)
		self.assertEqual(email.to, to)
		self.assertEqual(email.body, content)


	def test_set_config_email_with_wrong_subtype(self):
		"""
			Generar un error por seleccionar un subtype incorrecto
		"""

		subject = "Titulo del mensaje"
		from_email = "admin@gmail.com"
		to = ['user1@gmail.com']
		content = "Saludos"
		wrong_subtype = "txt"

		with self.assertRaisesMessage(ValueError, "Debe ser un subtype correcto: ['text', 'html']"):
			email = ConfigEmail.set_config(
				subject = subject,
				from_email = from_email,
				to = to,
				content = content,
				subtype = wrong_subtype
			)


	def test_set_config_email_without_from_email(self):
		"""
			Generar un error por no definir quien enviará el email
		"""
		subject = "Titulo del mensaje"
		to = ['user1@gmail.com']
		content = "Saludos"

		with self.assertRaisesMessage(ValueError, "Debe indicar de parte de quien será enviado el email"):
			email = ConfigEmail.set_config(
				subject = subject,
				to = to,
				content = content
			)



	def test_set_config_email_without_recipient_mailing(self):
		"""
			Generar un error por no definir la lista de destinatarios
		"""
		subject = "Titulo del mensaje"
		from_email = "admin@gmail.com"
		content = "Saludos"

		with self.assertRaisesMessage(ValueError, "Debe pasar una lista correos distinatario(s)"):
			email = ConfigEmail.set_config(
				subject = subject,
				from_email = from_email,
				content = content
			)


	def test_set_config_email_with_wrong_format_recipient_mailing(self):
		"""
			Generar un error por definir de manera incorrecta la lista de destinatarios
		"""
		subject = "Titulo del mensaje"
		from_email = "admin@gmail.com"
		to = 'user1@gmail.com'
		content = "Saludos"

		with self.assertRaisesMessage(ValueError, "Debes pasar una lista o tupla con los correos destinatarios"):
			email = ConfigEmail.set_config(
				subject = subject,
				from_email = from_email,
				to = to,
				content = content
			)
