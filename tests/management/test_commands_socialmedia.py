
from rest_framework import exceptions

from tests import faker
from tests.school.utils import create_social_media
from  .utils import testcases

from apps.management.apiv1.school import serializers


class CommandCreateSocialMedia(testcases.BasicCommandTestCase):

	def setUp(self):
		super().setUp()

		self.new_social_media = {
			"profile": faker.url()
		}

		self.new_list_social_media = {
			"profiles": [
				faker.url()
				for _ in range(5)
			]
		} 

	def test_create_socialmedia(self):
		"""
			Validar registrar red social a una escuela
		"""
		serializer = serializers.MSchoolSocialMediaResquest(
			data = self.new_social_media,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		social_media = serializer.save()

		self.assertTrue(social_media.id)
		self.assertEqual(social_media.profile, self.new_social_media["profile"])
		self.assertEqual(social_media.school_id, self.school.id)


	def test_bulk_create_socialmedia(self):
		"""
			Validar registrar multiples redes sociales a una escuela
		"""

		serializer = serializers.MSchoolSocialMediaResquest(
			data = self.new_list_social_media,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		list_social_media = serializer.save()

		self.assertTrue(list_social_media)

		for social_media in list_social_media:
			self.assertTrue(social_media.id)
			self.assertEqual(social_media.school_id, self.school.id)


	def test_create_socialmedia_with_wrong_url(self):
		"""
			Generar un error por enviar una url invalida
		"""
		self.new_social_media.update({"profile": faker.url()[2:]})

		serializer = serializers.MSchoolSocialMediaResquest(
			data = self.new_social_media,
			context = {"pk": self.school.id}
		)

		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)


	def test_create_socialmedia_already_exist(self):
		"""
			Generar un error por intentar registrar nuevamente una red social 
		"""
		created_social_media = create_social_media(school = self.school)

		self.new_social_media.update({"profile": created_social_media.profile})

		serializer = serializers.MSchoolSocialMediaResquest(
			data = self.new_social_media,
			context = {"pk": self.school.id}
		)

		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)


	def test_bulk_create_socialmedia_already_exist(self):
		"""
			Generar un error por intentar registrar nuevamente una red social.
		"""
		created_social_media = create_social_media(school = self.school)

		profiles = self.new_list_social_media["profiles"]
		profiles.append(created_social_media.profile)

		self.new_list_social_media.update({"profiles": profiles})

		serializer = serializers.MSchoolSocialMediaResquest(
			data = self.new_list_social_media,
			context = {"pk": self.school.id}
		)

		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)


	def test_create_socialmedia_with_school_does_not_exist(self):
		"""
			Generar un error por enviar el ID de una escuela que no existe
		"""
		wrong_school_id = faker.random_int(min = self.school.id + 1)

		serializer = serializers.MSchoolSocialMediaResquest(
			data = self.new_social_media,
			context = {"pk": wrong_school_id}
		)

		serializer.is_valid(raise_exception = True)

		with self.assertRaises(exceptions.ValidationError):
			serializer.save()
			