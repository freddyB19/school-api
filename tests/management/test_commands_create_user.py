import pprint

from django.test import TransactionTestCase, RequestFactory

from tests import faker

from rest_framework import exceptions

from apps.management import models 
from apps.user import models as user_models
from apps.management.apiv1.user import serializers

from tests.user.utils.utils import create_user

from .utils import testcases, testcases_data

class CommandCreateUserTest(testcases.CommandCreateUserTestCase):
	def setUp(self):
		super().setUp()

		self.request = RequestFactory().get("/", HTTP_X_SCHOOL_SUBDOMAIN = self.school.subdomain)
				
		password = faker.password()

		self.new_user = {
			"name": faker.name(),
			"email": faker.email(),
			"password": password,
			"password_confirm": password
		}

	def test_command_create(self):
		"""
			Validar función para crear un usuario
		"""

		serializer = serializers.AdminCreateUserSerializer(
			data = self.new_user,
			context = {"request": self.request}
		)

		serializer.is_valid(raise_exception = True)

		user = serializer.save()

		user_role_staff = user_models.TypeRole.staff

		self.assertTrue(user.id)
		self.assertEqual(user.name, self.new_user["name"])
		self.assertEqual(user.email, self.new_user["email"])
		self.assertEqual(user.role, user_role_staff)

		user_in_admin = models.Administrator.objects.filter(
			users__id = user.id, 
			school__subdomain = self.school.subdomain
		).exists()

		self.assertTrue(user_in_admin)

	def test_command_create_with_wrong_data(self):
		"""
			Generar un error por crear un usuario con datos invalidos
			- password: Not match, too short
			- name: too long, too short
		"""

		test_cases = testcases_data.CREATE_USER_WITH_WRONG_DATA

		for case in test_cases:
			with self.subTest(case = case):
				new_user = case["input"]["userInput"]

				serializer = serializers.AdminCreateUserSerializer(
					data = new_user,
					context = {"request": self.request}
				)

				with self.assertRaises(exceptions.ValidationError):
					serializer.is_valid(raise_exception = True)

				user_isnot_in_admin = models.Administrator.objects.filter(
					users__email = new_user["email"], 
					school__subdomain = self.school.subdomain
				).exists()

				self.assertFalse(user_isnot_in_admin)

	def test_command_create_with_wrong_school_subdomain(self):
		"""
			Generar un error por enviar el 'subdominio' de una escula no registrada
		"""
		wrong_subdomain = f"{faker.domain_word()}-{faker.pyint()}"
		request = RequestFactory().get("/", HTTP_X_SCHOOL_SUBDOMAIN = wrong_subdomain)

		serializer = serializers.AdminCreateUserSerializer(
			data = self.new_user,
			context = {"request": request}
		)
		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)

		user_isnot_in_admin = models.Administrator.objects.filter(
			users__email = self.new_user["email"], 
			school__subdomain = wrong_subdomain
		).exists()

		self.assertFalse(user_isnot_in_admin)

	def test_command_create_without_header(self):
		"""
			Generar un error por no enviar el 'subdominio' en el header
		"""
		request = RequestFactory().get("/")
				
		serializer = serializers.AdminCreateUserSerializer(
			data = self.new_user,
			context = {"request": request}
		)

		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)

		user_isnot_in_admin = models.Administrator.objects.filter(
			users__email = self.new_user["email"], 
			school__subdomain = self.school.subdomain
		).exists()

		self.assertFalse(user_isnot_in_admin)

	def test_command_create_with_existent_email(self):
		"""
			Generar un error por crear un usuario con un email ya registrado
		"""
		EMAIL = faker.email()

		create_user(email = EMAIL)

		self.new_user.update({"email": EMAIL})

		serializer = serializers.AdminCreateUserSerializer(
			data = self.new_user,
			context = {"request": self.request}
		)

		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)

		user_isnot_in_admin = models.Administrator.objects.filter(
			users__email = self.new_user["email"], 
			school__subdomain = self.school.subdomain
		).exists()

		self.assertFalse(user_isnot_in_admin)
