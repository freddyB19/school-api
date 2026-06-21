"""
	Funciones (commands) que forman parte de la creación 
	de un objeto 'CultutalEventMedia' - 'CultutalEvent'
"""
import pprint

from rest_framework import exceptions

from pydantic import ValidationError

from apps.school import models
from apps.management.commands import commands
from apps.management.apiv1.school import serializers

from tests import faker
from .utils import testcases, testcases_data, list_upload_files, create_list_files
from tests.school.utils import create_cultural_event

class CommandAddCulturalEventMediaTest(testcases.BasicCommandTestCase):
	def test_command_add_cultural_event_media(self):
		"""
			Validar agregar archivos en 'cultural-event-media'
		"""
		files = list_upload_files(size = 5, type_file = "image")
		total_files = len(files)

		command = commands.add_cultural_event_media(media = files)

		result = command.query
		status = command.status

		self.assertTrue(status)

		total_count = len(result)
		
		self.assertEqual(total_count, total_files)

		if result:
			self.assertIsInstance(result[0], models.CulturalEventMedia)

	def test_command_add_media_with_wrong_data(self):
		"""
			Generar un error por enviar datos invalidos
		"""

		files = create_list_files(size = 3, type_file = "image")

		with self.assertRaises(ValidationError):
			commands.add_cultural_event_media(media = files)


class CommandCreateCulturalEventTest(testcases.BasicCommandTestCase):
	def setUp(self):
		super().setUp()

		self.add_cultural_event = {
			"title": faker.text(max_nb_chars = models.MAX_LENGTH_CULTURALEVENT_TITLE),
			"description": faker.paragraph(),
			"date": faker.date_this_year(),
			"media": list_upload_files(size = 4, type_file = "image")
		}

	def test_command_create_culturalevent(self):
		"""
			Validar crear un registro para evento cultural
		"""

		serializer = serializers.MSchoolCulturalEventRequest(
			data = self.add_cultural_event,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)
		cultural_event = serializer.save()

		self.assertTrue(cultural_event)
		self.assertEqual(cultural_event.school_id, self.school.id)
		self.assertEqual(cultural_event.title, self.add_cultural_event["title"])
		self.assertEqual(cultural_event.description, self.add_cultural_event["description"])

		if self.add_cultural_event.get("media"):
			self.assertEqual(
				cultural_event.media.count(), 
				len(self.add_cultural_event["media"])
			)

	def test_command_create_culturalevent_without_description(self):
		"""
			Validar crear un registro para evento cultural sin descripción
		"""

		self.add_cultural_event.pop("description")

		serializer = serializers.MSchoolCulturalEventRequest(
			data = self.add_cultural_event,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)
		cultural_event = serializer.save()

		self.assertTrue(cultural_event)
		self.assertEqual(cultural_event.school_id, self.school.id)
		self.assertEqual(cultural_event.title, self.add_cultural_event["title"])
		self.assertIsNone(cultural_event.description)
		
		if self.add_cultural_event.get("media"):
			self.assertEqual(
				cultural_event.media.count(), 
				len(self.add_cultural_event["media"])
			)

	def test_command_create_culturalevent_without_media(self):
		"""
			Validar crear un registro para evento cultural sin 'media' (imágene(s))
		"""
		self.add_cultural_event.pop("media")
		without_images = 0

		serializer = serializers.MSchoolCulturalEventRequest(
			data = self.add_cultural_event,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)
		cultural_event = serializer.save()

		self.assertTrue(cultural_event)
		self.assertEqual(cultural_event.school_id, self.school.id)
		self.assertEqual(cultural_event.title, self.add_cultural_event["title"])
		self.assertEqual(cultural_event.description, self.add_cultural_event["description"])
		
		if not self.add_cultural_event.get("media"):
			self.assertEqual(
				cultural_event.media.count(), 
				without_images
			)

	def test_command_create_culturalevent_with_data_already_exist(self):
		"""
			Generar un error por intentar crear registros duplicados
		"""
		cultural_event = create_cultural_event(school = self.school)
		self.add_cultural_event.update({
			"title": cultural_event.title,
			"date": cultural_event.date
		})

		serializer = serializers.MSchoolCulturalEventRequest(
			data = self.add_cultural_event,
			context = {"pk": self.school.id}
		)
		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)

	def test_command_create_culturalevent_with_wrong_data(self):
		"""
			Generar error por enviar datos invalidos
		"""

		test_case = testcases_data.CREATE_CULTURAL_EVENT_WITH_WRONG_DATA

		for case in test_case:
			with self.subTest(case = case):
				serializer = serializers.MSchoolCulturalEventRequest(
					data = case,
					context = {"pk": self.school.id}
				)
				with self.assertRaises(exceptions.ValidationError):
					serializer.is_valid(raise_exception = True)

	def test_command_create_culturalevent_with_does_not_exist_school(self):
		"""
			Generar un error por intentar crear un registro con un ID de escuela invalida
		"""
		wrong_school_id = faker.random_int(
			min = models.School.objects.last().id + 1
		)

		serializer = serializers.MSchoolCulturalEventRequest(
			data = self.add_cultural_event,
			context = {"pk": wrong_school_id}
		)

		serializer.is_valid(raise_exception = True)
		
		with self.assertRaises(exceptions.ValidationError):
			cultural_event = serializer.save()
