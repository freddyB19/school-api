import pprint

from django.urls import reverse

from apps.management import models

from tests import faker
from tests.user.utils.utils import create_user

from .utils import testcases, testcases_data

class AdministratorCreateUserTest(testcases.AdminCreateUserTestCase):

	def setUp(self):
		super().setUp()

		self.URL_CREATE_USER = reverse("management:user-create")

		password = faker.password()

		self.add_user = {
			"name": faker.name(),
			"email": faker.email(),
			"password": password,
			"password_confirm": password
		}

	def test_create_user(self):
		"""
			Validar "POST /user" por crear un usuario
		"""
		response = self.client.post(
			self.URL_CREATE_USER,
			self.add_user,
			HTTP_X_SCHOOL_SUBDOMAIN = self.school.subdomain
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 201)

		self.assertTrue(responseJson)
		self.assertTrue(responseJson["id"])
		self.assertEqual(responseJson["name"], self.add_user["name"])
		self.assertEqual(responseJson["email"], self.add_user["email"])
		self.assertEqual(responseJson["school"]["subdomain"], self.school.subdomain)

		user_in_admin = models.Administrator.objects.filter(
			users__id = responseJson["id"],
			school__subdomain = self.school.subdomain
		).exists()

		self.assertTrue(user_in_admin)

	def test_create_user_without_header(self):
		"""
			Generar [Error 400] "POST /user" por no enviar el 'subdominio' en la cabecera
		"""
		response = self.client.post(
			self.URL_CREATE_USER,
			self.add_user
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 400)

		user_isnot_in_admin = models.Administrator.objects.filter(
			users__email = self.add_user["email"],
			school__subdomain = self.school.subdomain
		).exists()

		self.assertFalse(user_isnot_in_admin)


	def test_create_user_with_wrong_subdomain(self):
		"""
			Generar [Error 400] "POST /user" por enviar un 'subdominio' que no existe
		"""
		wrong_subdomain = f"{faker.domain_word()}-{faker.pyint()}"
		
		response = self.client.post(
			self.URL_CREATE_USER,
			self.add_user,
			HTTP_X_SCHOOL_SUBDOMAIN = wrong_subdomain
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 400)

		user_isnot_in_admin = models.Administrator.objects.filter(
			users__email = self.add_user["email"],
			school__subdomain = self.school.subdomain
		).exists()

		self.assertFalse(user_isnot_in_admin)

	def test_create_user_with_wrong_data(self):
		"""
			Generar [Error 400] "POST /user" por crear un usuario con datos invalidos
			- password: Not match, too short
			- name: too long, too short
		"""

		test_case = testcases_data.CREATE_USER_WITH_WRONG_DATA

		for case in test_case:
			with self.subTest(case = case):
				add_user = case['input']['userInput']
				
				response = self.client.post(
					self.URL_CREATE_USER,
					add_user,
					HTTP_X_SCHOOL_SUBDOMAIN = self.school.subdomain
				)

				responseJson = response.data
				responseStatusCode = response.status_code

				self.assertEqual(responseStatusCode, 400)

				user_isnot_in_admin = models.Administrator.objects.filter(
					users__email = self.add_user["email"],
					school__subdomain = self.school.subdomain
				).exists()

				self.assertFalse(user_isnot_in_admin)


	def test_create_user_with_existent_email(self):
		"""
			Generar [Error 400] "POST /user" por crear un usuario con un email ya registrado
		"""
		EMAIL = faker.email()

		create_user(email = EMAIL)

		self.add_user.update({"email": EMAIL})

		response = self.client.post(
			self.URL_CREATE_USER,
			self.add_user,
			HTTP_X_SCHOOL_SUBDOMAIN = self.school.subdomain
		)

		responseJson = response.data
		responseStatusCode = response.status_code
		
		self.assertEqual(responseStatusCode, 400)

		user_isnot_in_admin = models.Administrator.objects.filter(
			users__email = self.add_user["email"],
			school__subdomain = self.school.subdomain
		).exists()

		self.assertFalse(user_isnot_in_admin)
