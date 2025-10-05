from django.test import TestCase

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from tests import faker


class RenderingEmailTemplateTestCase(TestCase):
	def setUp(self):
		self.email = EmailMultiAlternatives(
			"Bienvenido",
			"Saludos",
			"fredd@gmail.com",
			["calors@gmail.com"],
		)

		self.basic_email_template = render_to_string(
			"emails/template_email_basic.html"
		)

class EmailServiceConfigTestCase(TestCase):
	def setUp(self):
		self.subject = faker.text(max_nb_chars = 20)
		self.from_email = faker.email()
		self.to = [faker.email()]
		self.content = faker.text(max_nb_chars = 20)


class RenderingEmailTemplateResetPasswordTestCase(TestCase):
	def setUp(self):
		self.template_name = 'reset_user_password.html'

		self.context_user = {
			"name_user": faker.name(),
			"password": faker.password()
		}

		self.emails_to = [faker.email()]