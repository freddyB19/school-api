import pprint

from django.urls import reverse

from tests import faker
from tests.user.utils import create_user

from .utils import testcases

class AdminLoginAPITest(testcases.AdminTokenTestCase):

	def setUp(self):
		super().setUp()

		self.URL_LOGIN = reverse(
			"management:login"
		)
		self.credentials = {"email": self.email, "password": self.password}

	def test_validate_login(self):
		"""
			Validar "POST /login"
		"""
		response = self.client.post(
			self.URL_LOGIN,
			self.credentials,
			HTTP_X_SCHOOL_SUBDOMAIN = self.school.subdomain
		)

		responseJson = response.data
		responseStatus = response.status_code


		self.assertEqual(responseStatus, 200)
		
		user = responseJson["user"]
		auth = responseJson["auth"]
		school = responseJson["school"]

		self.assertTrue(auth["access"])
		self.assertTrue(auth["refresh"])

		self.assertEqual(user["id"], self.user.id)
		self.assertEqual(user["email"], self.user.email)

		self.assertEqual(school["id"], self.school.id)
		self.assertEqual(school["subdomain"], self.school.subdomain)
		self.assertEqual(school["name"], self.school.name)


	def test_validate_login_with_wrong_credentials(self):
		"""
			Generar [Error 401] "POST /login" por credenciales invalidas
		"""
		self.credentials.update({"email": faker.email()})

		response = self.client.post(
			self.URL_LOGIN,
			self.credentials,
			HTTP_X_SCHOOL_SUBDOMAIN = self.school.subdomain
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)

		self.credentials.update({"password": faker.password()})

		response = self.client.post(
			self.URL_LOGIN,
			self.credentials,
			HTTP_X_SCHOOL_SUBDOMAIN = self.school.subdomain
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


	def test_validate_login_without_header(self):
		"""
			Generar [Error 400] "POST /login" por no enviar identificación en el HEADER
		"""
		response = self.client.post(
			self.URL_LOGIN,
			self.credentials
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)

	def test_validate_login_with_wrong_user(self):
		"""
			Generar [Error 400] "POST /login" por usuario que no pertenece a la administracción de la escuela 
		"""
		EMAIL = faker.email()
		PASSWORD = faker.password()

		user = create_user(email = EMAIL, password = PASSWORD)

		response = self.client.post(
			self.URL_LOGIN,
			{"email": EMAIL, "password": PASSWORD},
			HTTP_X_SCHOOL_SUBDOMAIN = self.school.subdomain
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)
