from django.urls import reverse

from apps.school import models

from tests import faker
from .utils import testcases, testcases_data
from tests.school.utils import (
	create_school, 
	create_social_media,
	bulk_create_social_media
)
from tests.user.utils import create_user, get_permissions


def get_create_list_socialmedia_url(school_id):
	return reverse(
		"management:socialmedia-list-create",
		kwargs = {"pk": school_id}
	)


def get_detail_socialmedia_url(id):
	return reverse(
		"management:socialmedia-detail",
		kwargs = {"pk": id}
	)

class SocialMediaCreateAPITest(testcases.SocialMediaCreateTestCase):
	def setUp(self):
		super().setUp()

		self.URL_SOCIALMEDIA_CREATE = get_create_list_socialmedia_url(
			school_id = self.school.id
		)

		self.add_profile = {
			"profile": faker.url()
		}

		self.add_profiles = {
			"profiles": [faker.url() for _ in range(5)]
		}

	def test_create_socialmedia(self):
		"""
			Validar "POST /socialmedia"
		"""

		self.client.force_authenticate(user = self.user_with_add_perm)

		response = self.client.post(
			self.URL_SOCIALMEDIA_CREATE,
			self.add_profile
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 201)
		self.assertTrue(responseJson["id"])
		self.assertEqual(responseJson["profile"], self.add_profile["profile"])

		# Validar "POST /socialmedia" enviado múltiples valores
		response = self.client.post(
			self.URL_SOCIALMEDIA_CREATE,
			self.add_profiles
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 201)
		self.assertTrue(responseJson)
		self.assertEqual(len(responseJson), len(self.add_profiles["profiles"]))


	def test_create_socialmedia_with_existent_profile(self):
		"""
			Generar [Error 400] "POST /socialmedia" por enviar un url ya registrada
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		socialmedia = create_social_media(school = self.school)
		self.add_profile.update({"profile": socialmedia.profile})

		response = self.client.post(
			self.URL_SOCIALMEDIA_CREATE,
			self.add_profile
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)

		# Generar [Error 400] Ahora con múltiples valores (incluyendo valor ya registrado)

		socialmedia = create_social_media(school = self.school)
		profiles = self.add_profiles["profiles"]
		profiles.append(socialmedia.profile)

		self.add_profiles.update({"profiles": profiles})

		response = self.client.post(
			self.URL_SOCIALMEDIA_CREATE,
			self.add_profiles
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 400)

	def test_create_socialmedia_without_school_permission(self):
		"""
			Generar [Error 403] "POST /socialmedia" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_add_perm)

		other_school = create_school()

		response = self.client.post(
			get_create_list_socialmedia_url(school_id = other_school.id),
			self.add_profiles
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_create_socialmedia_without_user_permission(self):
		"""
			Generar [Error 403] "POST /socialmedia" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.post(
			self.URL_SOCIALMEDIA_CREATE,
			self.add_profile
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_create_socialmedia_with_wrong_user(self):
		"""
			Generar [Error 403] "POST /socialmedia" por usuario que no pertenece a la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["add_socialmedia"])
		)

		self.client.force_authenticate(user = user)

		response = self.client.post(
			self.URL_SOCIALMEDIA_CREATE,
			self.add_profile
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_create_socialmedia_without_authentication(self):
		"""
			Generar [Error 401] "POST /socialmedia" usuario sin autenticar
		"""
		response = self.client.post(
			self.URL_SOCIALMEDIA_CREATE,
			self.add_profiles
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)



class SocialMediaListAPITest(testcases.SocialMediaTestCase):
	def setUp(self):
		super().setUp()

		self.URL_SOCIALMEDIA_LIST = get_create_list_socialmedia_url(
			school_id = self.school.id
		)

		bulk_create_social_media(size = 5, school = self.school)

	def test_get_socialmedia(self):
		"""
			Validar "GET /socialmedia"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		total_socialmedia = models.SocialMedia.objects.filter(
			school_id = self.school.id
		).count()

		response = self.client.get(self.URL_SOCIALMEDIA_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["count"], total_socialmedia)


	def test_get_socialmedia_without_school_permission(self):
		"""
			Generar [Error 403] "GET /socialmedia" de escuela que no tiene permiso de acceder
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_school = create_school()

		response = self.client.get(
			get_create_list_socialmedia_url(
				school_id = other_school.id
			)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_get_socialmedia_without_authentication(self):
		"""
			Generar [Error 401] "GET /socialmedia" usuario sin autenticar 
		"""
		response = self.client.get(self.URL_SOCIALMEDIA_LIST)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)



class SocialMediaDetailAPITest(testcases.SocialMediaDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.social_media = create_social_media(school = self.school)

		self.URL_SOCIALMEDIA_DETAIL = get_detail_socialmedia_url(
			id = self.social_media.id
		)

	def test_detail_socialmedia(self):
		"""
			Validar "GET /socialmedia/:id"
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		response = self.client.get(self.URL_SOCIALMEDIA_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.social_media.id)
		self.assertEqual(responseJson["profile"], self.social_media.profile)

	def test_get_socialmedia_without_school_permission(self):
		"""
			Generar [Error 403] "GET /socialmedia/:id" por información que pertenece a otra escuela
		"""
		self.client.force_authenticate(user = self.user_with_all_perm)

		other_social_media = create_social_media(school = create_school())

		response = self.client.get(
			get_detail_socialmedia_url(id = other_social_media.id)
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_get_socialmedia_with_wrong_user(self):
		"""
			Generar [Error 403] "GET /socialmedia/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()

		self.client.force_authenticate(user = user)

		response = self.client.get(self.URL_SOCIALMEDIA_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)


	def test_get_socialmedia_without_authentication(self):
		"""
			Generar [Error 401] "GET /socialmedia/:id" sin autenticación
		"""
		response = self.client.get(self.URL_SOCIALMEDIA_DETAIL)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class SocialMediaDeleteAPITest(testcases.SocialMediaDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.social_media = create_social_media(school = self.school)

		self.URL_SOCIALMEDIA_DELETE = get_detail_socialmedia_url(
			id = self.social_media.id
		)


	def test_delete_socialmedia(self):
		"""
			Validar "DELETE /socialmedia/:id"
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		response = self.client.delete(self.URL_SOCIALMEDIA_DELETE)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 204)

	def test_delete_socialmedia_without_school_permission(self):
		"""	
			Generar [Error 403] "DELETE /socialmedia/:id" por información que pertenece a otra escuela
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)

		other_social_media = create_social_media(school = create_school())

		response = self.client.delete(
			get_detail_socialmedia_url(id = other_social_media.id)
		)

		responseStatus = response.status_code
		
		self.assertEqual(responseStatus, 403)


	def test_delete_socialmedia_without_user_permission(self):
		"""
			Generar [Error 403] "DELETE /socialmedia/:id" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		response = self.client.delete(self.URL_SOCIALMEDIA_DELETE)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_socialmedia_with_wrong_user(self):
		"""
			Generar [Error 403] "DELETE /socialmedia/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["delete_socialmedia"])
		)

		self.client.force_authenticate(user = user)

		response = self.client.delete(self.URL_SOCIALMEDIA_DELETE)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_delete_socialmedia_without_authentication(self):
		"""
			Generar [Error 401] "DELETE /socialmedia/:id" sin autenticación
		"""
		response = self.client.delete(self.URL_SOCIALMEDIA_DELETE)

		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)


class SocialMediaUpdateAPITest(testcases.SocialMediaDetailDeleteUpdateTestCase):
	def setUp(self):
		super().setUp()

		self.social_media = create_social_media(school = self.school)

		self.URL_SOCIALMEDIA_UPDATE = get_detail_socialmedia_url(
			id = self.social_media.id
		)
		
		self.update_profile = {
			"profile": faker.url()
		}


	def test_update_socialmedia(self):
		"""
			Validar "PUT/PATCH /socialmedia/:id"
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)
		
		response = self.client.patch(
			self.URL_SOCIALMEDIA_UPDATE,
			self.update_profile
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 200)
		self.assertEqual(responseJson["id"], self.social_media.id)
		self.assertNotEqual(responseJson["profile"], self.social_media.profile)
		self.assertEqual(responseJson["profile"], self.update_profile["profile"])


	def test_update_socialmedia_with_wrong_data(self):
		"""
			Generar [Error 400] "PUT/PATCH /socialmedia/:id" por enviar datos invalidos
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		test_case = testcases_data.UPDATE_SOCIALMEDIA_WITH_WRONG_DATA

		for case in test_case:
			with self.subTest(case = case):
				response = self.client.patch(
					self.URL_SOCIALMEDIA_UPDATE,
					case
				)

				responseJson = response.data
				responseStatus = response.status_code
				
				self.assertEqual(responseStatus, 400)

	def test_update_socialmedia_without_school_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /socialmedia/:id" por información que pertenece a otra escuela
		"""
		self.client.force_authenticate(user = self.user_with_change_perm)

		other_social_media = create_social_media(school = create_school())

		response = self.client.patch(
			get_detail_socialmedia_url(id = other_social_media.id),
			self.update_profile
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_update_socialmedia_without_user_permission(self):
		"""
			Generar [Error 403] "PUT/PATCH /socialmedia/:id" por usuario sin permiso
		"""
		self.client.force_authenticate(user = self.user_with_delete_perm)
		
		response = self.client.patch(
			self.URL_SOCIALMEDIA_UPDATE,
			self.update_profile
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_update_socialmedia_with_wrong_user(self):
		"""
			Generar [Error 403] "PUT/PATCH /socialmedia/:id" por usuario que no forma parte de la administración de la escuela
		"""
		user = create_user()
		user.user_permissions.set(
			get_permissions(codenames = ["change_socialmedia"])
		)

		self.client.force_authenticate(user = user)
		
		response = self.client.patch(
			self.URL_SOCIALMEDIA_UPDATE,
			self.update_profile
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 403)

	def test_update_socialmedia_without_authentication(self):
		"""
			Generar [Error 401] "PUT/PATCH /socialmedia/:id" sin autenticación
		"""
		response = self.client.patch(
			self.URL_SOCIALMEDIA_UPDATE,
			self.update_profile
		)

		responseJson = response.data
		responseStatus = response.status_code

		self.assertEqual(responseStatus, 401)