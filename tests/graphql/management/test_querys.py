import pprint

from apps.management import models

from tests import faker

from .utils import testcases, utils


class AdministratorDetailQueryTest(testcases.AdminDetailQueryTestCase):

	def test_get_detail_administrator(self):
		"""
			Validar obtener el detalle de una administración
		"""
		total_admins = len(self.administrator.users.all())

		result = self.client.query(
			self.query,
			headers = self.headers,
			variables = self.variables,
		)

		self.assertIsNone(result.errors)
		
		response = result.data.get("administrator")

		self.assertTrue(response)
		self.assertEqual(response["id"], str(self.administrator.id))
		self.assertEqual(response["school"]["id"], str(self.school.id))
		self.assertEqual(response["users"]["totalCount"], total_admins)
	
	def test_get_administrator_when_does_not_exist(self):
		"""
			Intentanto obtener el detalle de una administración que no existe
		"""
		last_admin_id = models.Administrator.objects.last().id
		
		self.variables.update({"pk": faker.random_int(min = last_admin_id + 1)})

		result = self.client.query(
			self.query,
			headers = self.headers,
			variables = self.variables,
		)

		self.assertIsNone(result.errors)

		response = result.data["administrator"]['messages']
		
		responseStatusCode = response[0]["code"]["status"]
		
		self.assertEqual(responseStatusCode, 403)

	def test_get_detail_administrator_with_wrong_user(self):
		"""
			Generar un error por intentar acceder a información que no se tiene permiso
		"""
		authorization = utils.authorization_user()

		self.headers['Authorization'] = f"Bearer {authorization['token']}"

		result = self.client.query(
			self.query,
			headers = self.headers,
			variables = self.variables,
		)

		response = result.data["administrator"]['messages']
		responseStatusCode = response[0]["code"]["status"]

		self.assertEqual(responseStatusCode, 403)

	def test_get_detail_administrator_without_authentication(self):
		"""
			Generar error por obtener detalle de una administración sin autenticar
		"""
		result = self.client.query(self.query, variables = self.variables)
		
		response = result.data["administrator"]['messages']
		responseStatusCode = response[0]["code"]["status"]

		self.assertEqual(responseStatusCode, 401)
