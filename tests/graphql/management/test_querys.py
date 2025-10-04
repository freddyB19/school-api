import json, pprint

from apps.management import models

from tests import faker

from .utils import testcases, schemas

class AdministratorDetailQueryTest(testcases.AdminDetailQueryTestCase):

	def test_get_detail_administrator_info(self):
		"""
			Validar obtener el detalle de una administración
		"""
		total_admins = self.administrator.users.count()

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
		self.assertEqual(len(admins), total_admins)

		admin = admins[0]['node']

		self.assertTrue(
			self.administrator.users.filter(id = admin["userId"]).exists()
		)

	
	def test_get_administrator_when_does_not_exist(self):
		"""
			Intentanto obtener el detalle de una administración que no existe
		"""
		admin_id = models.Administrator.objects.last().id
		
		# Nos basamos en el último ID y le sumamos 1, para generar un ID falso
		variables = {
			"pk": faker.random_int(min = admin_id + 1),
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