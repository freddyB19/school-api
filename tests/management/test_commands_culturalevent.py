"""
	Funciones (commands) que forman parte de la creación 
	de un objeto 'CultutalEventMedia'
"""
import pprint

from pydantic import ValidationError

from apps.school import models
from apps.management.commands import commands

from tests import faker
from .utils import testcases, list_upload_files, create_list_files


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
