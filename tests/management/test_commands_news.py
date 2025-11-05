"""
	Funciones (commands) que forman parte de la creación 
	de un objeto 'News'
"""
import unittest, base64

from django.core.files.uploadedfile import SimpleUploadedFile


from rest_framework import exceptions

from pydantic import ValidationError

from PIL import Image

from tests import faker

from apps.school import models
from apps.management.commands import commands
from apps.management.apiv1.school import serializers

from .utils import testcases

from .utils import create_list_images, list_upload_images


class CommandAddNewsMediaTest(testcases.BasicCommandTestCase):

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


class CommandCreateNewsTest(testcases.BasicCommandTestCase):
	def setUp(self):
		super().setUp()

		self.data_news = {
			"title": faker.text(max_nb_chars=20),
			"description": faker.paragraph(),
			"media": list_upload_images(size = 2)
		}


	def test_create_a_news(self):
		"""
			Validar crear una noticia
		"""

		serializer = serializers.MSchoolNewsRequest(
			data = self.data_news,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		news = serializer.save()
		
		self.assertTrue(news)
		self.assertEqual(news.school_id, self.school.id)
		self.assertEqual(news.title, self.data_news["title"])
		self.assertEqual(news.description, self.data_news["description"])
		self.assertEqual(news.status, models.News.TypeStatus.published)

		self.assertEqual(news.media.count(), len(self.data_news["media"]))


	def test_create_news_without_images(self):
		"""
			Validar crear una noticia sin enviar imagenes
		"""

		self.data_news.pop("media")

		serializer = serializers.MSchoolNewsRequest(
			data = self.data_news,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		news = serializer.save()

		self.assertTrue(news)
		self.assertEqual(news.school_id, self.school.id)
		self.assertEqual(news.title, self.data_news["title"])
		self.assertEqual(news.description, self.data_news["description"])
		self.assertEqual(news.status, models.News.TypeStatus.published)

		total_images = 0
		
		self.assertEqual(news.media.count(), total_images)


	def test_create_news_with_wrong_data(self):
		"""
			Enviar datos invalidos para crear una noticia
		"""
		test_cases = [
			{
				"title": faker.pystr(
					max_chars = models.MIN_LENGTH_NEWS_TITLE - 1
				)
			},
			{
				"title": faker.pystr(
					max_chars = models.MAX_LENGTH_NEWS_TITLE + 1
				)
			},
			{
				"title": faker.text(max_nb_chars=20),
				"status": faker.text(max_nb_chars = 20)
			},
		]

		for case in test_cases:
			with self.subTest(case = case):
				serializer = serializers.MSchoolNewsRequest(
					data = case,
					context = {"pk": self.school.id}
				)

				with self.assertRaises(exceptions.ValidationError):
					serializer.is_valid(raise_exception = True)


	def test_create_news_with_non_existent_school(self):
		"""
			Enviar un ID de escuela que no existe
		"""
		wrong_school_id = self.school.id + 1

		serializer = serializers.MSchoolNewsRequest(
			data = self.data_news,
			context = {"pk": wrong_school_id}
		)

		serializer.is_valid(raise_exception = True)

		with self.assertRaises(exceptions.ValidationError):

			news = serializer.save()