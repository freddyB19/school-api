import json

from graphene_django.utils.testing import GraphQLTestCase

from apps.management.models import Administrator
from apps.user.tests.utils.utils import bulk_create_user
from apps.school.tests.utils.utils import create_school

class AdministratorDetailQueryTest(GraphQLTestCase):

	def setUp(self):
		self.school = create_school()
		self.users = bulk_create_user(total_users = 11)

		self.administrator = Administrator.objects.get(school_id = self.school.id)

		self.administrator.users.set(self.users)

		self.query_administrator_detail = """
			query AdministratorDetail($pk: Int!, $first: Int){

				detail(pk: $pk){
					id
					school {
						id
						name
					}
				}

				admins(pk: $pk, first: $first){
					pageInfo {
				        startCursor
				        endCursor
				        hasNextPage
				        hasPreviousPage
				    }
				    edges {
				        cursor
				        node {
							name
							email
							role
							userId
							dateJoined
							lastLogin
				        }
			        }
				}
			}
		"""
		self.variables_administrator_detail = {
			"pk": self.administrator.id,
			"first": 2
		}


	def test_get_detail_administrator_info(self):
		"""
			El detalle de una administración
		"""

		result = self.query(
			self.query_administrator_detail,
			variables = self.variables_administrator_detail
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

		query = """
			query AdministratorDetail($pk: Int!, $first: Int, $after: String){

				admins(pk: $pk, first: $first, after: $after){
					pageInfo {
				        startCursor
				        endCursor
				        hasNextPage
				        hasPreviousPage
				    }
				    edges {
				        cursor
				        node {
				            id
							name
							email
				        }
			        }
				}
			}
		"""

		variables = {
			"pk": self.administrator.id,
			"after": response["data"]["admins"]["pageInfo"]["endCursor"],
			"first": 3
		}

		result = self.query(
			query,
			variables = variables
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
			variables = variables
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