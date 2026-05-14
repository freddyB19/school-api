"""
	Funciones (commands) que forman parte de la creación 
	de un objeto 'Download'
"""

import pprint

from django.utils import timezone

from rest_framework import exceptions

from pydantic import ValidationError

from apps.school import models
from apps.management.apiv1.school import serializers

from tests import faker
from tests.school.utils.utils import create_download
from .utils import testcases, list_upload_files, create_list_files

class CommandCreateDownloadTest(testcases.BasicCommandTestCase):
	def setUp(self):
		super().setUp()

		self.add_download = {
			"name": faker.text(max_nb_chars = models.MAX_LENGTH_DOWNLOAD_NAME),
			"description": faker.paragraph(),
			"media": list_upload_files(type_file = "office")[0]
		}

	def test_create_download(self):
		"""
			Validar crear un archivo para 'download' 
		"""
		serializer = serializers.MSchoolDownloadRequest(
			data = self.add_download,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		download = serializer.save()

		self.assertTrue(download)
		self.assertEqual(download.name, self.add_download["name"])
		self.assertEqual(download.description, self.add_download["description"])

		if self.add_download["media"]:
			self.assertTrue(download.file)


	def test_create_download_without_description(self):
		"""
			Validar crear un archivo 'download' sin descripción
		"""

		self.add_download.pop("description")

		serializer = serializers.MSchoolDownloadRequest(
			data = self.add_download,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		download = serializer.save()

		self.assertTrue(download)
		self.assertEqual(download.name, self.add_download["name"])
		self.assertIsNone(download.description)

		if self.add_download["media"]:
			self.assertTrue(download.file)

	def test_create_download_without_name(self):
		"""
			Validar crear un archivo 'download' sin nombre
		"""

		self.add_download.pop("name")

		serializer = serializers.MSchoolDownloadRequest(
			data = self.add_download,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		download = serializer.save()

		self.assertTrue(download)
		self.assertTrue(download.name)
		self.assertEqual(download.description, self.add_download["description"])

		if self.add_download["media"]:
			self.assertTrue(download.file)

	def test_create_download_with_name_already_exists(self):
		"""
			Generar un error por enviar ya registrados
		"""
		download = create_download(school = self.school)

		self.add_download["name"] = download.name

		serializer = serializers.MSchoolDownloadRequest(
			data = self.add_download,
			context = {"pk": self.school.id}
		)
		
		with self.assertRaises(exceptions.ValidationError):

			serializer.is_valid(raise_exception = True)

	def test_create_download_with_wrong_data(self):
		"""
			Generar un error por enviar datos invalidos
		"""

		self.add_download.update({
			"media": create_list_files(type_file = "office")
		})

		serializer = serializers.MSchoolDownloadRequest(
			data = self.add_download,
			context = {"pk": self.school.id}
		)

		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)

	def test_create_download_with_does_not_exist_school(self):
		"""
			Generar un error por enviar el ID de una escuela que no existe
		"""
		wrong_school_id = faker.random_int(
			min = models.School.objects.last().id + 1
		)

		serializer = serializers.MSchoolDownloadRequest(
			data = self.add_download,
			context = {"pk": wrong_school_id}
		)

		serializer.is_valid(raise_exception = True)
		
		with self.assertRaises(exceptions.ValidationError):
			serializer.save()
