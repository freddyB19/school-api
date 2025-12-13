"""
	Funciones (commands) que forman parte de la creación 
	de un objeto 'Repository'
"""
import unittest, pprint

from pydantic import ValidationError

from tests import faker

from apps.management.commands import commands

from .utils import testcases, list_upload_files, create_list_files


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
