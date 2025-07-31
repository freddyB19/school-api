import json

from faker import Faker
from graphene_django.utils.testing import GraphQLTestCase

from apps.school.tests.utils.utils import create_school
from apps.user.tests.utils.utils import FakerCreateUser, create_user

faker = Faker(locale="es")

class AdministratorUserMutationTest(GraphQLTestCase):
	def setUp(self):
		self.faker_user = FakerCreateUser()
		self.school = create_school()
		self.user = create_user()

		self.query_create_user = """
			mutation CreateUser($school_id: Int!, $user: UserInput!){
				createUser(schoolId: $school_id, user: $user){
					user {
						id
						name
						email
						role
					}
				}
			}
		"""
		self.variables_create_user = {
			"school_id": self.school.id,
			"user": {
				"name": self.faker_user.name,
				"email": self.faker_user.email, 
				"password": self.faker_user.password, 
				"passwordConfirm": self.faker_user.password
			}
		}

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

		self.assertEqual(
			response["data"]["createUser"]["user"]["name"], 
			self.variables_create_user["user"]["name"],
		)
		self.assertEqual(
			response["data"]["createUser"]["user"]["email"], 
			self.variables_create_user["user"]["email"],
		)

	def test_create_user_with_wrong_school_ID(self):
		"""
			Genearar un error por enviar el ID de una escuela que no existe
		"""

		wrong_school_id = 120
		self.variables_create_user.update({"school_id": wrong_school_id})

		result = self.query(
			self.query_create_user,
			variables = self.variables_create_user
		)

		response = json.loads(result.content)

		self.assertEqual(response["errors"][0]["message"], "No existe una escuela con ese ID")


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

		self.assertEqual(response["errors"][0]["message"], "Error en los datos enviados")
		self.assertEqual(
			response["errors"][0]["extensions"]["invalidArguments"]["email"], 
			["Ya existe un usuario con este email"]
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

		self.assertEqual(
			response["errors"][0]["extensions"]["invalidArguments"]["non_field_errors"], 
			["Las contraseñas no coinciden"]
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
		
		self.assertEqual(
			response["errors"][0]["extensions"]["invalidArguments"]["password"], 
			["La contraseña es muy corta"]
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
		
		self.assertEqual(
			response["errors"][0]["extensions"]["invalidArguments"]["name"], 
			["El nombre es muy corto"]
		)

	def test_create_user_with_to_long_name(self):
		"""
			Intentar crear un usuario con un nombre muy largo
		"""
		new_user = self.variables_create_user["user"]
		long_name = f"{faker.paragraph(nb_sentences = 5)}{faker.paragraph(nb_sentences = 5)}"
		new_user.update({"name": long_name})

		self.variables_create_user.update({"user": new_user})

		result = self.query(
			self.query_create_user,
			variables = self.variables_create_user
		)

		response = json.loads(result.content)
		
		self.assertEqual(
			response["errors"][0]["extensions"]["invalidArguments"]["name"], 
			["El nombre de usuario es muy largo"]
		)
