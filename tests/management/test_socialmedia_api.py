from django.urls import reverse

from tests import faker
from .utils import testcases
from tests.school.utils import (
	create_school, 
	create_social_media 
)
from tests.user.utils import create_user, get_permissions


def get_create_list_socialmedia_url(school_id):
	return reverse(
		"management:socialmedia-list-create",
		kwargs = {"pk": school_id}
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