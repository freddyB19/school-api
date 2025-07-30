import unittest

from django.urls import reverse
from django.test import TransactionTestCase

from rest_framework.test import APIClient
from rest_framework.test import force_authenticate

from apps.management.apiv1 import views
from apps.management import models

from apps.user.tests.utils.utils import create_user
from apps.school.tests.utils.utils import create_school

from .utils.utils import get_administrator

class AdministratorAPITest(TransactionTestCase):

	def setUp(self):
		self.client = APIClient()

		self.school = create_school()
		self.user_role_admin = create_user(role = 0)
		self.user_role_staff = create_user(role = 1, email = "carlos@example.com")
		self.administrator = get_administrator(school_id = self.school.id)
		self.administrator.users.set([self.user_role_admin, self.user_role_staff])


		self.URL_ADMINISTRATOR = reverse(
			"management:administrator", 
			kwargs={"school_id": self.school.id}
		) 
		self.URL_ADMINISTRATOR_DETAIL = reverse(
			"management:administrator-detail", 
			kwargs={"pk": self.administrator.id}
		)


	def test_get_administrator(self):
		"""
			Validar endpoint administrator
		"""

		response = self.client.get(self.URL_ADMINISTRATOR)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.administrator.id)
		self.assertLessEqual(len(responseJson["users"]), 5)
		self.assertEqual(responseJson["total_users"], self.administrator.users.count())


	def test_get_administrator_with_no_existent_school(self):
		"""
			Intentar acceder a la información de 'administrator' con un ID de escuela que no existe
		"""
		wrong_school_id = 100
		
		response = self.client.get(reverse(
			"management:administrator", 
			kwargs={"school_id": wrong_school_id}
		))

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)
		self.assertEqual(responseJson["error"]["message"], f"No existe información sobre los administradores del portal de un colegio con ID: {wrong_school_id}")


	def test_get_detail_administrator(self):
		"""
			Validar endpoint administrator-detail
		"""

		response = self.client.get(self.URL_ADMINISTRATOR_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.administrator.id)
		self.assertEqual(responseJson["total_users"], self.administrator.users.count())
		self.assertEqual(responseJson["school"]["id"], self.school.id)
		self.assertEqual(responseJson["school"]["name"], self.school.name)


	def test_get_detail_administrator_does_not_exist(self):
		"""
			Intentar acceder a una información que no existe en endpoint administrator-detail
		"""
		wrong_id = 120
		
		response = self.client.get(reverse(
			"management:administrator-detail", 
			kwargs={"pk": wrong_id}
		))

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 404)
		self.assertEqual(responseJson["error"]["message"], f"No existe información sobre los administradores de este portal con ID: {wrong_id}")