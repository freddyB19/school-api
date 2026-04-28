"""
	Funciones (commands) que forman parte de la creación 
	de un objeto 'Infraestructure'
"""
import pprint

from .utils import testcases

from rest_framework import exceptions

from pydantic import ValidationError

from apps.school import models
from apps.management.commands import commands
from apps.management.apiv1.school import serializers


from tests import faker
from tests.school.utils import create_infraestructure
from .utils import testcases, testcases_data, list_upload_files, create_list_files


class CommandAddInfraestructureMediaTest(testcases.BasicCommandTestCase):
	
	def test_command_add_infra_media(self):
		"""
			Validar crear archivos en 'infraestructure-media'
		"""
		files = []
		files.extend(list_upload_files(size = 3, type_file = "image"))
		total_files = len(files)

		list_files = commands.add_infraestructure_media(media = files)

		self.assertTrue(list_files.status)

		total_infra_media = len(list_files.query)
		
		self.assertEqual(total_infra_media, total_files)

	def test_command_add_infra_media_with_wrong_data(self):
		"""
			Generar un error por enviar una lista de datos invalidos
		"""
		files = create_list_files(size = 6, type_file = "image")

		with self.assertRaises(ValidationError):
			commands.add_infraestructure_media(media = files)


class CommandCreateInfraestructureTest(testcases.BasicCommandTestCase):
	def setUp(self):
		super().setUp()

		files = []
		files.extend(list_upload_files(size = 5, type_file = "image"))

		self.add_infraestructure = {
			"name": faker.text(max_nb_chars = models.MAX_LENGTH_INFRA_NAME),
			"description": faker.paragraph(),
			"media": files,
		}

	def test_command_create_infraestructure(self):
		""" 
			Validar crear datos sobre 'infraestructura' de una escuela
		"""
		serializer = serializers.MSchoolInfraestructureRequest(
			data = self.add_infraestructure,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		infraestructure = serializer.save()

		self.assertTrue(infraestructure)
		self.assertEqual(infraestructure.name, self.add_infraestructure["name"])
		self.assertEqual(infraestructure.description, self.add_infraestructure["description"])
		
		if self.add_infraestructure["media"]:
			total_files = len(self.add_infraestructure["media"])
			self.assertEqual(infraestructure.media.count(), total_files)

	
	def test_command_create_infraestructure_without_description(self):
		"""
			Validar crear datos sobre 'infraestructura' sin una descripción
		"""
		self.add_infraestructure.pop("description")

		serializer = serializers.MSchoolInfraestructureRequest(
			data = self.add_infraestructure,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		infraestructure = serializer.save()

		self.assertTrue(infraestructure)
		self.assertEqual(infraestructure.name, self.add_infraestructure["name"])
		self.assertIsNone(infraestructure.description)
		
		if self.add_infraestructure["media"]:
			total_files = len(self.add_infraestructure["media"])
			self.assertEqual(infraestructure.media.count(), total_files)

	def test_command_create_infraestructure_without_media(self):
		"""
			Validar crear datos sobre 'infraestructura' sin imágenes
		"""
		without_images = 0
		self.add_infraestructure.pop("media")

		serializer = serializers.MSchoolInfraestructureRequest(
			data = self.add_infraestructure,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		infraestructure = serializer.save()

		self.assertTrue(infraestructure)
		self.assertEqual(infraestructure.name, self.add_infraestructure["name"])
		self.assertEqual(infraestructure.description, self.add_infraestructure["description"])
		self.assertEqual(infraestructure.media.count(), without_images)

	def test_command_create_infraestructure_with_data_already_exist(self):
		"""
			Generar un error por crear datos con un mismo nombre
		"""
		infraestructure = create_infraestructure(school = self.school)

		self.add_infraestructure.update({"name": infraestructure.name})

		serializer = serializers.MSchoolInfraestructureRequest(
			data = self.add_infraestructure,
			context = {"pk": self.school.id}
		)

		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)

	def test_command_create_infraestructure_with_wrong_data(self):
		"""
			Generar un error por enviar datos invalidos
		"""
		test_cases = testcases_data.CREATE_INFRAESTRUCTURE_WITH_WRONG_DATA

		for case in test_cases:
			with self.subTest(case = case):
				serializer = serializers.MSchoolInfraestructureRequest(
					data = case,
					context = {"pk": self.school.id}
				)

				with self.assertRaises(exceptions.ValidationError):
					serializer.is_valid(raise_exception = True)

	def test_command_create_infraestructure_with_does_not_exist_school(self):
		"""
			Generar un error por enviar el ID de una escuela que no existe
		"""
		wrong_school_id = faker.random_int(min = models.School.objects.last().id + 1)

		serializer = serializers.MSchoolInfraestructureRequest(
			data = self.add_infraestructure,
			context = {"pk": wrong_school_id}
		)

		serializer.is_valid(raise_exception = True)

		with self.assertRaises(exceptions.ValidationError):
			serializer.save()
