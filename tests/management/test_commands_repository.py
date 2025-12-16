"""
	Funciones (commands) que forman parte de la creación 
	de un objeto 'Repository'
"""
import unittest, pprint

from rest_framework import exceptions

from pydantic import ValidationError

from apps.school import models
from apps.management.commands import commands
from apps.management.apiv1.school import serializers

from tests import faker
from tests.school.utils import create_repository
from .utils import testcases, testcases_data, list_upload_files, create_list_files


class CommandAddRepositoryMediaTest(testcases.BasicCommandTestCase):

	def test_add_repositorymedia(self):
		"""
			Validar crear archivos en 'repository'
		"""
		files = []

		files.extend(list_upload_files(size = 3, type_file = "office"))
		files.extend(list_upload_files(size = 2, type_file = "image"))

		list_files = commands.add_repository_media(media = files)

		self.assertTrue(list_files)
		self.assertEqual(len(list_files), len(files))

	def test_add_repositorymedia_with_wrong_data(self):
		"""
			Generar un error por enviar una lista de datos invalidos
		"""

		files = create_list_files(size = 5, type_file = "image")

		with self.assertRaises(ValidationError):
			list_files = commands.add_repository_media(media = files)


class CommandCreateRepository(testcases.BasicCommandTestCase):
	def setUp(self):
		super().setUp()

		files = []
		files.extend(list_upload_files(size = 3, type_file = "office"))
		files.extend(list_upload_files(size = 3, type_file = "image"))

		self.add_repository = {
			"name_project": faker.text(max_nb_chars = models.MAX_LENGTH_REPOSITORY_NAME_PROJECT),
			"description": faker.paragraph(),
			"media": files,
		}

	def test_create_repository(self):
		"""
			Validar crear un 'repositorio' para una escuela
		"""
		serializer = serializers.MSchoolRepositoryRequest(
			data = self.add_repository,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		repository = serializer.save()
		self.assertTrue(repository)
		self.assertEqual(repository.name_project, self.add_repository["name_project"])
		self.assertEqual(repository.description, self.add_repository["description"])
		self.assertEqual(repository.media.count(), len(self.add_repository["media"]))

	def test_create_repository_without_description(self):
		"""
			Validar crear un 'repositorio' sin una descripción
		"""
		self.add_repository.pop("description")

		serializer = serializers.MSchoolRepositoryRequest(
			data = self.add_repository,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		repository = serializer.save()

		self.assertTrue(repository)
		self.assertIsNone(repository.description)
		self.assertEqual(repository.name_project, self.add_repository["name_project"])
		self.assertEqual(repository.media.count(), len(self.add_repository["media"]))

	def test_create_repository_without_media(self):
		"""
			Validar crear un 'repositorio' sin archivos
		"""
		self.add_repository.pop("media")
		total_repository_media = 0

		serializer = serializers.MSchoolRepositoryRequest(
			data = self.add_repository,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		repository = serializer.save()

		self.assertTrue(repository)
		self.assertEqual(repository.name_project, self.add_repository["name_project"])
		self.assertEqual(repository.description, self.add_repository["description"])
		self.assertEqual(repository.media.count(), total_repository_media)
	
	def test_create_repository_with_data_already_exists(self):
		"""
			Generar un error por enviar datos ya registrados
		"""
		repository = create_repository(school = self.school)

		self.add_repository.update({
			"name_project": repository.name_project
		})

		serializer = serializers.MSchoolRepositoryRequest(
			data = self.add_repository,
			context = {"pk": self.school.id}
		)

		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)

	def test_create_repository_with_wrong_data(self):
		"""
			Generar un error por enviar datos invalidos
		"""
		test_case = testcases_data.CREATE_REPOSITORY_WITH_WRONG_DATA

		for case in test_case:
			with self.subTest(case = case):
				serializer = serializers.MSchoolRepositoryRequest(
					data = case,
					context = {"pk": self.school.id}
				)

				with self.assertRaises(exceptions.ValidationError):
					serializer.is_valid(raise_exception = True)

	def test_create_repository_does_not_exit_school(self):
		"""
			Generar un error por enviar el ID de una escuela que no existe
		"""
		wrong_school_id = faker.random_int(min = self.school.id + 1)

		serializer = serializers.MSchoolRepositoryRequest(
			data = self.add_repository,
			context = {"pk": wrong_school_id}
		)

		serializer.is_valid(raise_exception = True)

		with self.assertRaises(exceptions.ValidationError):
			serializer.save()
