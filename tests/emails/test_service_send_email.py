from apps.emails.services.send_email import ConfigEmail, ContentHTMLMessage

from tests import faker

from .utils import testcases


class ConfigEmailServiceTest(testcases.EmailServiceConfigTestCase):

	def test_set_config_email(self):
		"""
			Validar configuraciones para un simple email
		"""
		email = ConfigEmail.set_config(
			subject = self.subject,
			from_email = self.from_email,
			to = self.to,
			content = self.content
		)

		self.assertEqual(email.content_subtype, "text")
		self.assertEqual(email.subject, self.subject)
		self.assertEqual(email.from_email, self.from_email)
		self.assertEqual(email.to, self.to)
		self.assertEqual(email.body, self.content)

	def test_set_config_email_with_template_message(self):
		"""
			Validar configuraciones para email con un template como mensaje
		"""
		template_name = "reset_user_password.html"
		context = {"name": faker.name(), "password": faker.password()}

		content = ContentHTMLMessage.set_message(
			template_name = template_name,
			context = context
		)
		
		email = ConfigEmail.set_config(
			subject = self.subject,
			from_email = self.from_email,
			to = self.to,
			content = content,
			subtype = "html"
		)

		self.assertEqual(email.content_subtype, "html")
		self.assertEqual(email.subject, self.subject)
		self.assertEqual(email.from_email, self.from_email)
		self.assertEqual(email.to, self.to)
		self.assertEqual(email.body, content)


	def test_set_config_email_with_wrong_subtype(self):
		"""
			Generar un error por seleccionar un subtype incorrecto
		"""
		wrong_subtype = "txt"

		with self.assertRaisesMessage(ValueError, "Debe ser un subtype correcto: ['text', 'html']"):
			email = ConfigEmail.set_config(
				subject = self.subject,
				from_email = self.from_email,
				to = self.to,
				content = self.content,
				subtype = wrong_subtype
			)


	def test_set_config_email_without_from_email(self):
		"""
			Generar un error por no definir quien enviará el email
		"""
		error_message = "Debe indicar de parte de quien será enviado el email"

		with self.assertRaisesMessage(ValueError, error_message):
			email = ConfigEmail.set_config(
				subject = self.subject,
				to = self.to,
				content = self.content
			)



	def test_set_config_email_without_recipient_mailing(self):
		"""
			Generar un error por no definir la lista de destinatarios
		"""
		with self.assertRaisesMessage(ValueError, "Debe pasar una lista correos distinatario(s)"):
			email = ConfigEmail.set_config(
				subject = self.subject,
				from_email = self.from_email,
				content = self.content
			)


	def test_set_config_email_with_wrong_format_recipient_mailing(self):
		"""
			Generar un error por definir de manera incorrecta la lista de destinatarios
		"""
		to = faker.email()

		with self.assertRaisesMessage(ValueError, "Debes pasar una lista o tupla con los correos destinatarios"):
			email = ConfigEmail.set_config(
				subject = self.subject,
				from_email = self.from_email,
				to = to,
				content = self.content
			)
