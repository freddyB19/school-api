import tempfile

from django.urls import reverse

from apps.school import models

from PIL import Image

from tests import faker

from tests.school.utils import (
	create_school,
	create_infraestructure,
	bulk_create_infraestructure
)

from tests.user.utils import create_user, get_permissions

from .utils import testcases, testcases_data

def get_list_create_infraestructure_url(school_id,**extra):
	return reverse(
		"management:infraestructure-list-create",
		kwargs={"pk": school_id},
		**extra
	)


class InfraestructureCreateAPITest(testcases.InfraestructureCreateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_INFRAESTRUCTURE_CREATE =  get_list_create_infraestructure_url(
			school_id = self.school.id
		)

		self.add_infraestructure = {
			"name": faker.text(max_nb_chars = models.MAX_LENGTH_INFRA_NAME),
			"description": faker.paragraph(),
		}

	def test_create_infraestructure(self):
		"""
			Validar "POST /infraestructure" 
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			self.add_infraestructure.update({"media": [ntf]})

			response = self.client.post(
				self.URL_INFRAESTRUCTURE_CREATE,
				self.add_infraestructure,
				format="multipart"
			)

			responseJson = response.data
			responseStatusCode = response.status_code

			self.assertEqual(responseStatusCode, 201)
			self.assertEqual(responseJson["name"], self.add_infraestructure["name"])
			self.assertEqual(responseJson["description"], self.add_infraestructure["description"])
			self.assertEqual(len(responseJson["media"]), len(self.add_infraestructure["media"]))

	def test_create_infraestructure_without_description(self):
		"""
			Validar "POST /infraestructure" sin 'descripción'  
		"""

		self.client.force_authenticate(user = self.user_with_add_perm)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			self.add_infraestructure.pop("description")
			self.add_infraestructure.update({"media": [ntf]})

			response = self.client.post(
				self.URL_INFRAESTRUCTURE_CREATE,
				self.add_infraestructure,
				format="multipart"
			)

			responseJson = response.data
			responseStatusCode = response.status_code

			self.assertEqual(responseStatusCode, 201)
			self.assertEqual(responseJson["name"], self.add_infraestructure["name"])
			self.assertIsNone(responseJson["description"])
			self.assertEqual(len(responseJson["media"]), len(self.add_infraestructure["media"]))

	def test_create_infraestructure_without_media(self):
		"""
			Validar "POST /infraestructure" sin 'imágenes'  
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		total_images = 0

		response = self.client.post(
			self.URL_INFRAESTRUCTURE_CREATE,
			self.add_infraestructure
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 201)
		self.assertEqual(responseJson["name"], self.add_infraestructure["name"])
		self.assertEqual(responseJson["description"], self.add_infraestructure["description"])
		self.assertEqual(len(responseJson["media"]), total_images)

	def test_create_infraestructure_with_wrong_data(self):
		"""
			Generar [Error 400] "POST /infraestructure" por enviar datos invalidos
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		test_cases = testcases_data.CREATE_INFRAESTRUCTURE_WITH_WRONG_DATA

		for case in test_cases:
			with self.subTest(case = case):
				response = self.client.post(
					self.URL_INFRAESTRUCTURE_CREATE,
					case
				)

				responseJson = response.data
				responseStatusCode = response.status_code

				self.assertEqual(responseStatusCode, 400)

		with tempfile.NamedTemporaryFile(suffix = ".jpg") as ntf:
			img = Image.new("RGB", (10, 10))
			img.save(ntf, format="JPEG")
			ntf.seek(0)

			ntf.name = f"/tmp/{faker.pystr(max_chars = models.MAX_LENGTH_INFRA_NAME + 1)}.jpg"

			self.add_infraestructure.update({"media": [ntf]})

			response = self.client.post(
				self.URL_INFRAESTRUCTURE_CREATE,
				self.add_infraestructure,
				format="multipart"
			)

			responseJson = response.data
			responseStatusCode = response.status_code

			self.assertEqual(responseStatusCode, 400)

	def test_create_infraestructure_with_data_already_exists(self):
		"""
			Generar [Error 400] "POST /infraestructure" por enviar datos ya registrados
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		infraestructure = create_infraestructure(school = self.school)

		self.add_infraestructure.update({"name": infraestructure.name})

		response = self.client.post(
			self.URL_INFRAESTRUCTURE_CREATE,
			self.add_infraestructure
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 400)

	def test_create_infraestructure_without_school_permission(self):
		"""
			Generar [Error 400] "POST /infraestructure" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		school = create_school()

		response = self.client.post(
			get_list_create_infraestructure_url(
				school_id = school.id
			),
			self.add_infraestructure
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_create_infraestructure_without_user_permission(self):
		"""
			Generar [Error 400] "POST /infraestructure" por usuario sin permisos
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.post(
			self.URL_INFRAESTRUCTURE_CREATE,
			self.add_infraestructure
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_create_infraestructure_with_wrong_user(self):
		"""
			Generar [Error 400] "POST /infraestructure" por usuario que no pertenece a la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ['add_infraestructure'])
		)

		self.client.force_authenticate(user = user)

		response = self.client.post(
			self.URL_INFRAESTRUCTURE_CREATE,
			self.add_infraestructure
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_create_infraestructure_without_authentication(self):
		"""
			Generar [Error 400] "POST /infraestructure" sin autenticación  
		"""
		response = self.client.post(
			self.URL_INFRAESTRUCTURE_CREATE,
			self.add_infraestructure
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)


class InfraestructureListAPITest(testcases.InfraestructureTestCase):
	def setUp(self):
		super().setUp()

		bulk_create_infraestructure(school = self.school, size = 6)

		self.URL_INFRAESTRUCTURE_LIST =  get_list_create_infraestructure_url(
			school_id = self.school.id
		)

	def test_get_infraestructure(self):
		"""
			Validar "GET /infraestructure"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		total_infraestructures = models.Infraestructure.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_INFRAESTRUCTURE_LIST)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["count"], total_infraestructures)

	def test_get_infraestructure_filter_by_name(self):
		"""
			Validar "GET /infraestructure?name=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		name = faker.word()

		create_infraestructure(
			school = self.school,
			name = f"{name} {faker.text(max_nb_chars = 20)}"
		)

		total_infraestructures = models.Infraestructure.objects.filter(
			school_id = self.school.id,
			name__icontains = name
		).count()

		response = self.client.get(
			get_list_create_infraestructure_url(
				school_id = self.school.id,
				query = {"name": name}
			)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 200)
		self.assertEqual(responseJson["count"], total_infraestructures)

	def test_get_infraestructure_without_school_permission(self):
		"""
			Generar [Error 403] "GET /infraestructure" de escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_school = create_school()

		response = self.client.get(
			get_list_create_infraestructure_url(
				school_id = other_school.id
			)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_get_infraestructure_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /infraestructure" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()
		permissions = get_permissions(codenames = [
			'add_infraestructure', 
			'change_infraestructure', 
			'delete_infraestructure', 
			'view_infraestructure'
		])

		user.user_permissions.set(permissions)

		self.client.force_authenticate(user = user)

		response = self.client.get(
			get_list_create_infraestructure_url(
				school_id = self.school.id
			)
		)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 403)

	def test_get_infraestructure_without_authentication(self):
		"""
			Generar [Error 401] "GET /infraestructure" sin autenticar
		"""

		response = self.client.get(self.URL_INFRAESTRUCTURE_LIST)

		responseJson = response.data
		responseStatusCode = response.status_code

		self.assertEqual(responseStatusCode, 401)
