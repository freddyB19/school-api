import json

from tests import faker

from .utils import testcases, utils
from apps.user.apiv1 import serializers
from apps.graphql.management_user.mutations import GraphQLErrorMessage


class AdministratorUserMutationTest(testcases.AdminCreateUserTestCase):

	def test_create_user(self):
		"""
			Validar que se ha creado un usuario
		"""
		result = self.query(
			self.query_create_user,
			variables = self.variables_create_user
		)

		self.assertResponseNoErrors(result)

		response = json.loads(result.content)

		user = response["data"]["createUser"]["user"]

		self.assertEqual(
			user["name"], 
			self.variables_create_user["user"]["name"],
		)
		self.assertEqual(
			user["email"], 
			self.variables_create_user["user"]["email"],
		)

	def test_create_user_with_wrong_school_ID(self):
		"""
			Enviando el ID de una escuela que no existe al intentar crear un usuario
		"""

		wrong_school_id = 120
		self.variables_create_user.update({"school_id": wrong_school_id})

		result = self.query(
			self.query_create_user,
			variables = self.variables_create_user
		)

		response = json.loads(result.content)

		user = response["data"]["createUser"]

		self.assertIsNone(user["user"])


	def test_create_user_with_existent_email(self):
		"""
			Intentar crear un usuario con un email ya registrado
		"""
		new_user = self.variables_create_user["user"]
		new_user.update({"email": self.user.email})

		self.variables_create_user.update({"user": new_user})

		result = self.query(
			self.query_create_user,
			variables = self.variables_create_user
		)

		response = json.loads(result.content)

		error_message = response["errors"][0]["message"]
		error_arguments = response["errors"][0]["extensions"]["invalidArguments"]

		self.assertEqual(error_message, GraphQLErrorMessage)
		self.assertEqual(
			error_arguments["email"], 
			[serializers.EMAIL_ALREADY_REGISTERED]
		)


	def test_create_user_with_not_match_password(self):
		"""
			Intentar crear un usuario con contraseñas que no coinciden
		"""
		new_user = self.variables_create_user["user"]
		new_user.update({"passwordConfirm": "abcdefghlj"})

		self.variables_create_user.update({"user": new_user})

		result = self.query(
			self.query_create_user,
			variables = self.variables_create_user
		)

		response = json.loads(result.content)

		error = response["errors"][0]["extensions"]["invalidArguments"]

		self.assertEqual(
			error["non_field_errors"], 
			[serializers.PASSWORDS_NOT_MATCH]
		)


	def test_create_user_with_to_shoort_password(self):
		"""
			Intentar crear un usuario con una contraseña muy corta
		"""
		new_user = self.variables_create_user["user"]
		new_user.update({"password": "abcd"})
		new_user.update({"passwordConfirm": "abcd"})

		self.variables_create_user.update({"user": new_user})

		result = self.query(
			self.query_create_user,
			variables = self.variables_create_user
		)

		response = json.loads(result.content)

		error = response["errors"][0]["extensions"]["invalidArguments"]
		
		self.assertEqual(
			error["password"], 
			[serializers.MIN_LEN_PASSWORD]
		)


	def test_create_user_with_to_shoort_name(self):
		"""
			Intentar crear un usuario con un nombre muy corto
		"""
		new_user = self.variables_create_user["user"]
		new_user.update({"name": "noe"})

		self.variables_create_user.update({"user": new_user})

		result = self.query(
			self.query_create_user,
			variables = self.variables_create_user
		)

		response = json.loads(result.content)
		
		error = response["errors"][0]["extensions"]["invalidArguments"]
		
		self.assertEqual(
			error["name"], 
			[serializers.MIN_LEN_NAME]
		)

	def test_create_user_with_to_long_name(self):
		"""
			Intentar crear un usuario con un nombre muy largo
		"""
		new_user = self.variables_create_user["user"]
		long_name = utils.GET_LONG_NAME()
		new_user.update({"name": long_name})

		self.variables_create_user.update({"user": new_user})

		result = self.query(
			self.query_create_user,
			variables = self.variables_create_user
		)

		response = json.loads(result.content)

		error = response["errors"][0]["extensions"]["invalidArguments"]
		
		self.assertEqual(
			error["name"], 
			[serializers.MAX_LEN_NAME]
		)
