import json

from django.test import Client
from django.contrib.auth import get_user_model

from graphene_django.utils.testing import GraphQLTestCase

from apps.management.models import Administrator
from apps.user.tests.utils.utils import bulk_create_user, create_user
from apps.school.tests.utils.utils import create_school

from apps.graphql.tests.utils import get_token

from .utils.schemas import (
	QUERY_ADMINISTRATOR_DETAIL,
	QUERY_ADMINISTRATOR_DETAIL_ADMINS
)

def authorization_user():
	EMAIL = "user_auth@example.com"
	PASSWORD = "12345678"

	user = create_user(email = EMAIL, password = PASSWORD)
	return get_token(email = EMAIL, password = PASSWORD)


class AdministratorDetailQueryTest(GraphQLTestCase):

	def setUp(self):
		self.client = Client()

		self.school = create_school()
		self.users = bulk_create_user(size = 11)
		token = authorization_user()
		self.headers = {
			"Authorization": f"Bearer {token}"
		}

		self.administrator = Administrator.objects.get(school_id = self.school.id)

		self.administrator.users.set(self.users)


		self.query_administrator_detail = QUERY_ADMINISTRATOR_DETAIL		
		self.variables_administrator_detail = {
			"pk": self.administrator.id,
			"first": 2
		}


	def test_get_detail_administrator_info(self):
		result = self.query(
			self.query_administrator_detail,
			variables = self.variables_administrator_detail,
			headers = self.headers
		)

		self.assertResponseNoErrors(result)

		response = json.loads(result.content)

		detail = response["data"]["detail"]
		admins = response["data"]["admins"]["edges"]

		self.assertEqual(int(detail["id"]), self.administrator.id)
		self.assertEqual(int(detail["school"]["id"]), self.school.id)

		self.assertEqual(
			len(admins), 
			self.variables_administrator_detail["first"]
		)

		query = QUERY_ADMINISTRATOR_DETAIL_ADMINS

		variables = {
			"pk": self.administrator.id,
			"after": response["data"]["admins"]["pageInfo"]["endCursor"],
			"first": 3
		}

		result = self.query(
			query,
			variables = variables,
			headers = self.headers
		)

		self.assertResponseNoErrors(result)

		response = json.loads(result.content)

		admins_next_page = response["data"]["admins"]["edges"]

		self.assertEqual(
			len(admins_next_page), 
			variables["first"]
		)


	def test_get_administrator_when_does_not_exist(self):
		"""
			Intentanto obtener el detalle de una administración que no existe
		"""

		variables = {
			"pk": 120,
			"first": 2
		}

		admins_total_elements = 0

		result = self.query(
			self.query_administrator_detail,
			variables = variables,
			headers = self.headers
		)

		self.assertResponseNoErrors(result)

		response = json.loads(result.content)

		detail = response["data"]["detail"]
		admins = response["data"]["admins"]
		
		self.assertIsNone(detail)
		self.assertEqual(
			len(admins["edges"]), 
			admins_total_elements
		)