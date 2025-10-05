"""
	Funciones (commands) que forman parte de la creación 
	de un objeto 'News'
"""
import unittest

from tests import faker
from pydantic import ValidationError

from apps.school import models
from apps.management.commands import commands
from .utils import testcases

from .utils import create_list_images, list_upload_images


class CommandAddNewsTest(testcases.CommandNewsTestCase):

	def test_add_news(self):
		"""
			Validar crear una noticia
		"""
		data_news = {
			"title": faker.text(max_nb_chars=20),
			"description": faker.paragraph()
		}

		news = commands.add_news(
			news = data_news, 
			school_id = self.school.id
		)

		self.assertTrue(news)
		self.assertEqual(news.title, data_news["title"])
		self.assertEqual(news.description, data_news["description"])
		self.assertEqual(news.school_id, self.school.id)
		self.assertEqual(news.status, models.News.TypeStatus.published)


	def test_add_news_with_wrong_data(self):
		"""
			Generar error por enviar datos invalidos
		"""

		test_cases = [
			{
				"title": "Text"
			},
			{
				"title": faker.text(max_nb_chars=200)
			},
			{
				"title": faker.text(max_nb_chars=20),
				"status": "pausado"
			},
		]

		for case in test_cases:
			with self.subTest(case = case):
				with self.assertRaises(ValidationError):
					commands.add_news(news = case, school_id = self.school.id)


	def test_add_news_without_school_id(self):
		"""
			Generar un error al no enviar el ID de una escuela
		"""
		data_news = {
			"title": faker.text(max_nb_chars=20),
			"description": faker.paragraph()
		}

		with self.assertRaises(ValidationError):
			news = commands.add_news(
				news = data_news, 
			)


class CommandAddNewsMediaTest(testcases.CommandNewsTestCase):

	def test_add_newsmedia(self):
		"""
			Validar crear 'newsmedia'
		"""
		images = list_upload_images(size = 3)

		list_newsmedia = commands.add_newsmedia(media = images)

		self.assertTrue(list_newsmedia)
		self.assertEqual(len(list_newsmedia), len(images))

		
	def test_add_newsmedia_with_wrong_data(self):
		"""
			Generar un error por enviar una lista de datos invalidos
		"""
		images = create_list_images()

		with self.assertRaises(ValidationError):
			list_newsmedia = commands.add_newsmedia(media = images)
	

	def test_add_newsmedia_without_list_images(self):
		"""
			Generar un error por no enviar lista de imagenes
		"""
		with self.assertRaises(ValidationError):
			commands.add_newsmedia()


class CommandCreateNewsTest(testcases.CommandNewsTestCase):
	def setUp(self):
		super().setUp()

		self.images = list_upload_images(size = 5)

		self.data_news = {
			"title": faker.text(max_nb_chars=20),
			"description": faker.paragraph()
		}


	def test_create_a_news(self):
		"""
			Validar crear una noticia
		"""
		command = commands.create_news(
			school_id = self.school.id, 
			news = self.data_news, 
			images = self.images
		)

		self.assertTrue(command.status)
		
		news_created = command.query

		self.assertTrue(news_created)
		self.assertEqual(news_created.school_id, self.school.id)
		self.assertEqual(news_created.title, self.data_news["title"])
		self.assertEqual(news_created.description, self.data_news["description"])
		self.assertEqual(news_created.status, models.News.TypeStatus.published)

		self.assertEqual(news_created.media.count(), len(self.images))


	def test_create_news_without_images(self):
		"""
			Validar crear una noticia sin enviar imagenes
		"""

		command = commands.create_news(
			school_id = self.school.id, 
			news = self.data_news,
		)

		self.assertTrue(command.status)
		
		news_created = command.query

		self.assertTrue(news_created)
		self.assertEqual(news_created.school_id, self.school.id)
		self.assertEqual(news_created.title, self.data_news["title"])
		self.assertEqual(news_created.description, self.data_news["description"])
		self.assertEqual(news_created.status, models.News.TypeStatus.published)

		self.assertEqual(news_created.media.count(), 0)


	def test_create_news_with_wrong_data(self):
		"""
			Enviar datos invalidos para crear una noticia
		"""
		test_cases = [
			{
				"title": "Text"
			},
			{
				"title": faker.text(max_nb_chars=200)
			},
			{
				"title": faker.text(max_nb_chars=20),
				"status": "pausado"
			},
		]

		for case in test_cases:
			with self.subTest(case = case):
				command = commands.create_news(
					images = self.images,
					school_id = self.school.id,
					news = case
				)

				self.assertFalse(command.status)
				self.assertFalse(command.query)
				self.assertGreaterEqual(len(command.errors), 1)


	def test_create_news_with_non_existent_school(self):
		"""
			Enviar un ID de escuela que no existe
		"""
		wrong_school_id = 12

		command = commands.create_news(
			images = self.images,
			school_id = wrong_school_id,
			news = self.data_news
		)

		self.assertFalse(command.status)
		self.assertFalse(command.query)
		self.assertGreaterEqual(len(command.errors), 1)


	@unittest.expectedFailure
	def test_create_news_without_school_id(self):
		"""
			No enviar el ID de una escuela
		"""
		commands.create_news(
			images = self.images,
			news = self.data_news
		)
			


	@unittest.expectedFailure
	def test_create_news_without_data_news(self):
		"""
			No enviar la información para la nueva noticia
		"""
		commands.create_news(
			images = self.images,
			school_id = self.school.id,
		)
			