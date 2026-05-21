import tempfile

from django.urls import reverse
from apps.school import models
from tests import faker

from tests.user.utils import create_user, get_permissions
from tests.school.utils import (
	create_school,
	create_download, 
	bulk_create_download 
)

from .utils import testcases, testcases_data

def get_create_list_download_url(school_id, **extra):
	return reverse(
		"management:download-list-create",
		kwargs = {"pk": school_id},
		**extra
	)


def get_detail_download_url(pk):
	return reverse(
		"management:download-detail",
		kwargs = {"pk": pk}
	)

class DownloadCreateAPITest(testcases.DownloadCreateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_DOWNLOAD_CREATE = get_create_list_download_url(
			school_id = self.school.id
		)

		self.add_download = {
			"name": faker.text(max_nb_chars = models.MAX_LENGTH_DOWNLOAD_NAME - 1),
			"description": faker.paragraph()
		}

	def test_create_download(self):
		"""
			Validar "POST /download"
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		with tempfile.NamedTemporaryFile(suffix = ".zip") as ntf:
			ntf.write(b"Datos del archivo")
			ntf.seek(0)

			self.add_download.update({"media": [ntf]})

			response = self.client.post(
				self.URL_DOWNLOAD_CREATE,
				self.add_download,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 201)
			self.assertEqual(responseJson["name"], self.add_download["name"])
			self.assertEqual(responseJson["description"], self.add_download["description"])

			if "media" in self.add_download:
				self.assertTrue(responseJson["file"])


	def test_create_download_without_description(self):
		"""
			Validar "POST /download" sin 'description'
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		with tempfile.NamedTemporaryFile(suffix = ".zip") as ntf:
			ntf.write(b"Datos del archivo")
			ntf.seek(0)

			self.add_download.update({"media": [ntf]})

			self.add_download.pop("description")

			response = self.client.post(
				self.URL_DOWNLOAD_CREATE,
				self.add_download,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 201)
			self.assertEqual(responseJson["name"], self.add_download["name"])
			self.assertIsNone(responseJson["description"])

			if "media" in self.add_download:
				self.assertTrue(responseJson["file"])

	def test_create_download_without_name(self):
		"""
			Validar "POST /download" sin 'name'
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		with tempfile.NamedTemporaryFile(suffix = ".zip") as ntf:
			ntf.write(b"Datos del archivo")
			ntf.seek(0)
			
			self.add_download.pop("name")

			self.add_download.update({"media": [ntf]})

			response = self.client.post(
				self.URL_DOWNLOAD_CREATE,
				self.add_download,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 201)
			self.assertTrue(responseJson["name"])
			self.assertEqual(responseJson["description"], self.add_download["description"])

			if "media" in self.add_download:
				self.assertTrue(responseJson["file"])

	def test_create_download_with_wrong_data(self):
		"""
			Generar [Error 400] "POST /download" por
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		test_cases = [
			{
				"name": faker.pystr(
					max_chars = models.MAX_LENGTH_DOWNLOAD_NAME + 1
				)
			},
			{
				"name": faker.pystr(
					max_chars = models.MIN_LENGTH_DOWNLOAD_NAME - 1
				)
			}
		]

		with tempfile.NamedTemporaryFile(suffix = ".zip") as ntf:
			ntf.write(b"Datos del archivo")
			ntf.seek(0)
			
			for case in test_cases:
				with self.subTest(case = case):
					case.update({"media": [ntf]})
					
					response = self.client.post(
						self.URL_DOWNLOAD_CREATE,
						case,
						format="multipart"
					)

					responseJson = response.data
					responseStatus = response.status_code

					self.assertEqual(responseStatus, 400)

	def test_create_download_without_user_permission(self):
		"""
			Generar [Error 403] "POST /download" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		with tempfile.NamedTemporaryFile(suffix = ".zip") as ntf:
			ntf.write(b"Datos del archivo")
			ntf.seek(0)

			self.add_download.update({"media": [ntf]})

			response = self.client.post(
				self.URL_DOWNLOAD_CREATE,
				self.add_download,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 403)

	def test_create_download_without_school_permission(self):
		"""
			Generar [Error 403] "POST /download"  de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		other_school = create_school()

		with tempfile.NamedTemporaryFile(suffix = ".zip") as ntf:
			ntf.write(b"Datos del archivo")
			ntf.seek(0)

			self.add_download.update({"media": [ntf]})

			response = self.client.post(
				get_create_list_download_url(school_id = other_school.id),
				self.add_download,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 403)

	def test_create_download_with_wrong_user(self):
		"""
			Generar [Error 403] "POST /download" por usuario que no pertenece a la administración de la escuela
		"""
		user = create_user()

		user.user_permissions.set(
			get_permissions(codenames = ["add_download"])
		)

		self.client.force_authenticate(user = user)

		with tempfile.NamedTemporaryFile(suffix = ".zip") as ntf:
			ntf.write(b"Datos del archivo")
			ntf.seek(0)

			self.add_download.update({"media": [ntf]})

			response = self.client.post(
				self.URL_DOWNLOAD_CREATE,
				self.add_download,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 403)

	def test_create_download_without_authentication(self):
		"""
			Generar [Error 401] "POST /download" sin autenticar
		"""
		with tempfile.NamedTemporaryFile(suffix = ".zip") as ntf:
			ntf.write(b"Datos del archivo")
			ntf.seek(0)

			self.add_download.update({"media": [ntf]})

			response = self.client.post(
				self.URL_DOWNLOAD_CREATE,
				self.add_download,
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 401)


class DownloadListAPITest(testcases.DownloadTestCase):
	def setUp(self):
		super().setUp()

		self.URL_DOWNLOAD_LIST = get_create_list_download_url(
			school_id = self.school.id
		)

		self.download = bulk_create_download(size = 10, school = self.school)

	def test_get_download(self):
		"""
			Validar "GET /download"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		total_downloads = models.Download.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_DOWNLOAD_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_downloads)

	def test_get_download_filter_by_name(self):
		"""
			Validar "GET /download?name=<...>"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		download_name = faker.word()

		create_download(
			school = self.school,
			name = f"{download_name} {faker.text(max_nb_chars = 15)}"
		)

		total_downloads = models.Download.objects.filter(
			school_id = self.school.id,
			name__icontains = download_name,
		).count()

		response = self.client.get(get_create_list_download_url(
			school_id = self.school.id,
			query = {"name": download_name}
		))

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_downloads)

	def test_get_download_without_school_permission(self):
		"""
			Generar [Error 403] "GET /download" de escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_school = create_school()

		response = self.client.get(
			get_create_list_download_url(school_id = other_school.id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_get_download_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /download" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(get_permissions(
			codenames = ["view_download"]
		))

		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_DOWNLOAD_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_get_download_without_authentication(self):
		"""
			Generar [Error 401] "GET /download" sin autenticar
		"""
		
		response = self.client.get(self.URL_DOWNLOAD_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class DownloadDetailAPITest(testcases.DownloadDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.download = create_download(school = self.school)

		self.URL_DOWNLOAD_DETAIL = get_detail_download_url(
			pk = self.download.id
		)

	def test_detail_download(self):
		"""
			Validar "GET /download/:id"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(self.URL_DOWNLOAD_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.download.id)
		self.assertEqual(responseJson["name"], self.download.name)

	def test_detail_download_without_school_permission(self):
		"""
			Generar [Error 403] "GET /download/:id" de escuela que no tiene permiso de acceder 
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		download = create_download()

		response = self.client.get(
			get_detail_download_url(pk = download.id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_detail_download_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /download/:id" por usuario que no forma parte de la administración
		"""
		user = create_user()

		user.user_permissions.set(
			get_permissions(codenames = ["view_download"])
		)

		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_DOWNLOAD_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_detail_download_without_authentication(self):
		"""
			Generar [Error 401] "GET /download/:id" sin autenticar
		"""
		response = self.client.get(self.URL_DOWNLOAD_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class DownloadDeleteAPITest(testcases.DownloadDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.download = create_download(school = self.school)

		self.URL_DOWNLOAD_DELETE = get_detail_download_url(
			pk = self.download.id
		)

	def test_delete_download(self):
		"""
			Validar "DELETE /download:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(self.URL_DOWNLOAD_DELETE)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 204)

	def test_delete_download_without_user_permission(self):
		"""
			Generar [Error 403] "DELETE /download/:id" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.delete(self.URL_DOWNLOAD_DELETE)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_download_without_school_permission(self):
		"""
			Generar [Error 403] "DELETE /download/:id" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		download = create_download()

		response = self.client.delete(
			get_detail_download_url(pk = download.id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_download_with_wrong_user(self):
		"""
			Generar [Error 403] "DELETE /download/:id" por usuario que no forma parte de la administración
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["delete_download"])
		)

		self.client.force_authenticate(user = user)

		response = self.client.delete(self.URL_DOWNLOAD_DELETE)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_download_without_authentication(self):
		"""
			Generar [Error 401] "DELETE /download/:id" sin autenticar
		"""
		response = self.client.delete(self.URL_DOWNLOAD_DELETE)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class DownloadUpdateAPITest(testcases.DownloadDetailDeleteUpdateTestCase):

	def setUp(self):
		super().setUp()

		self.download = create_download(school = self.school)

		self.URL_DOWNLOAD_UPDATE = get_detail_download_url(
			pk = self.download.id
		)

		self.partial_download = {
			"description": faker.paragraph()
		}

		self.update_download = {
			"name": faker.text(max_nb_chars = models.MAX_LENGTH_DOWNLOAD_NAME - 1),
			"description": faker.paragraph()
		}

	def test_update_download(self):
		"""
			Validar "PUT/PATCH /download/:id"
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.patch(
			self.URL_DOWNLOAD_UPDATE,
			self.update_download,
		)

		responseJson = response.data
		responseStatus = response.status_code
		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.download.id)
		self.assertNotEqual(responseJson["name"], self.download.name)
		self.assertNotEqual(responseJson["description"], self.download.description)
		
		self.assertEqual(responseJson["name"], self.update_download["name"])
		self.assertEqual(responseJson["description"], self.update_download["description"])


		response = self.client.patch(
			self.URL_DOWNLOAD_UPDATE,
			self.partial_download
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.download.id)
		self.assertNotEqual(responseJson["description"], self.download.description)
		self.assertEqual(responseJson["description"], self.partial_download["description"])

	def test_update_download_with_name_already_exists(self):
		"""
			Generar [Error 400] "PUT/PATCH /download/:id" por datos ya registrados
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		download = create_download(school = self.school)

		update_name = {"name": download.name}

		response = self.client.patch(
			self.URL_DOWNLOAD_UPDATE,
			update_name
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)

	def test_update_download_with_wrong_data(self):
		"""
			Generar [Error 400] "PUT/PATCH /download/:id" por enviar datos invalidos
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		test_cases = [
			{
				"name": faker.pystr(
					max_chars = models.MAX_LENGTH_DOWNLOAD_NAME + 1
				)
			},
			{
				"name": faker.pystr(
					max_chars = models.MIN_LENGTH_DOWNLOAD_NAME - 1
				)
			}
		]

		for case in test_cases:
			with self.subTest(case = case):
				response = self.client.patch(
					self.URL_DOWNLOAD_UPDATE,
					case
				)

				responseJson = response.data
				responseStatus = response.status_code

				self.assertEqual(responseStatus, 400)

	def test_update_download_without_school_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /download/:id" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		download = create_download()

		response = self.client.patch(
			get_detail_download_url(
				pk = download.id
			),
			self.update_download
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_update_download_without_user_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /download/:id" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.patch(
			self.URL_DOWNLOAD_UPDATE,
			self.partial_download
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_update_download_with_wrong_user(self):
		"""
			Generar [Error 403] "PUT/PATCH /download/:id" por usuario que no forma parte de la administración
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["change_download"])
		)

		self.client.force_authenticate(user = user)

		response = self.client.patch(
			self.URL_DOWNLOAD_UPDATE,
			self.partial_download
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)
	
	def test_update_download_without_authentication(self):
		"""
			Generar [Error 401] "PUT/PATCH /download/:id" sin autenticar
		"""

		response = self.client.patch(
			self.URL_DOWNLOAD_UPDATE,
			self.update_download,
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class DownloadUpdateFileAPITest(testcases.DownloadDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.download = create_download(school = self.school)

		self.URL_DOWNLOAD_UPDATE_FILE = self.get_update_download_file_url(
			pk = self.download.id
		)

	def get_update_download_file_url(self, pk):
		return reverse(
			"management:download-file",
			kwargs={"pk": pk}
		)

	def test_update_download_file(self):
		"""
			Validar "PATCH /download/file/:id"
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		with tempfile.NamedTemporaryFile(suffix = ".zip") as ntf:
			ntf.write(b"Datos del archivo")
			ntf.seek(0)

			response = self.client.patch(
				self.URL_DOWNLOAD_UPDATE_FILE,
				{"media": [ntf]},
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 202)

	def test_update_download_file_without_user_permission(self):
		"""
			Generar [Error 403] "PATCH /download/file/:id" por usuario sin permiso
		"""

		self.client.force_authenticate(user = self.user_with_delete_perm)

		with tempfile.NamedTemporaryFile(suffix = ".zip") as ntf:
			ntf.write(b"Datos del archivo")
			ntf.seek(0)

			response = self.client.patch(
				self.URL_DOWNLOAD_UPDATE_FILE,
				{"media": [ntf]},
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 403)

	def test_update_download_file_with_wrong_method(self):
		"""
			Generar [Error 405] "PATCH /download/file/:id" por método incorrecto
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		with tempfile.NamedTemporaryFile(suffix = ".zip") as ntf:
			ntf.write(b"Datos del archivo")
			ntf.seek(0)

			response = self.client.put(
				self.URL_DOWNLOAD_UPDATE_FILE,
				{"media": [ntf]},
				format="multipart"
			)

			responseJson = response.data
			responseStatus = response.status_code

			self.assertEqual(responseStatus, 405)
