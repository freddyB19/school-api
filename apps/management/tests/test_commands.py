import unittest, random, datetime

from django.utils.datastructures import MultiValueDict
from django.core.files.uploadedfile import SimpleUploadedFile

from . import faker
from pydantic import ValidationError

from apps.school import models
from apps.management.commands import commands
from apps.management.commands.utils.errors_messages import (
	TimeGroupErrorsMessages,
	OfficeHourErrorsMessages
)

from .utils.testcases import (
	CommandNewsTest,
	CommandTimeGroupTest,
	CommandOfficeHourTest,
)
from .utils.utils import create_list_images, list_upload_images
from apps.school.tests.utils.utils import create_daysweek


class CommandAddNewsTest(CommandNewsTest):

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


class CommandAddNewsMediaTest(CommandNewsTest):

	def test_add_newsmedia(self):
		"""
			Validar crear 'newsmedia'
		"""
		images = [
			SimpleUploadedFile(
				"test_image1.jpg", 
				content=b"content_image1", 
				content_type="image/jpeg"
			),
			SimpleUploadedFile(
				"test_image2.jpg", 
				content=b"content_image2", 
				content_type="image/jpeg"
			),
			SimpleUploadedFile(
				"test_image3.jpg", 
				content=b"content_image3", 
				content_type="image/jpeg"
			),
		]

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

		for image in images:
			image.close()
	

	def test_add_newsmedia_without_list_images(self):
		"""
			Generar un error por no enviar lista de imagenes
		"""
		with self.assertRaises(ValidationError):
			commands.add_newsmedia()


class CommandCreateNewsTest(CommandNewsTest):
	def setUp(self):
		super().setUp()

		self.images = MultiValueDict({"media": list_upload_images()})

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

		self.assertEqual(news_created.media.count(), len(self.images.getlist("media")))


	def test_create_news_without_images(self):
		"""
			Validar crear una noticia sin enviar imagenes
		"""

		command = commands.create_news(
			school_id = self.school.id, 
			news = self.data_news,
			images = MultiValueDict()
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
			

class CommandAddTimeGroupTest(CommandTimeGroupTest):

	def setUp(self):
		super().setUp()
		self.new_time_group = {
			"type": faker.text(
				max_nb_chars = models.MAX_LENGTH_TYPEGROUP_TYPE
			),
			"opening_time": datetime.time(7, 30),
			"closing_time": datetime.time(14, 30),
			"active": random.choice([True, False]),
			"overview": faker.paragraph(),
		}
	
	def test_add_time_group(self):
		"""
			Validar crear un 'TimeGroup'
		"""

		daysweek = faker.random_elements(
			length=4, 
			unique=True,
			elements=[1,2,3,4,5], 
		)

		self.new_time_group.update({"daysweek": daysweek})

		time_group = commands.add_time_group(
			time_group = self.new_time_group,
		)

		self.assertTrue(time_group)
		self.assertTrue(time_group.id)
		self.assertEqual(time_group.type, self.new_time_group["type"])
		self.assertEqual(time_group.active, self.new_time_group["active"])
		self.assertGreaterEqual(time_group.daysweek.count(), 1)


	def test_add_time_group_without_daysweek(self):
		"""
			Validar crear un 'TimeGroup' sin enviar 'daysweek'
		"""
		time_group = commands.add_time_group(
			time_group = self.new_time_group,
		)

		self.assertTrue(time_group)
		self.assertTrue(time_group.id)
		self.assertEqual(time_group.type, self.new_time_group["type"])
		self.assertEqual(time_group.active, self.new_time_group["active"])
		self.assertEqual(time_group.daysweek.count(), 0)


	def test_add_time_group_without_overview(self):
		"""
			Validar crear un 'TimeGroup' sin enviar 'overview'
		"""
		self.new_time_group.pop("overview")

		time_group = commands.add_time_group(
			time_group = self.new_time_group,
		)

		self.assertTrue(time_group)
		self.assertTrue(time_group.id)
		self.assertEqual(time_group.type, self.new_time_group["type"])
		self.assertEqual(time_group.active, self.new_time_group["active"])
		self.assertEqual(time_group.daysweek.count(), 0)

	def test_add_time_group_without_time(self):
		"""
			Generar un error por no enviar [opening_time, closing_time]
		"""
		self.new_time_group.pop("opening_time")

		with self.assertRaises(ValidationError):
			commands.add_time_group(
				time_group = self.new_time_group,
			)
		
		self.new_time_group.pop("closing_time")

		with self.assertRaises(ValidationError):
			commands.add_time_group(
				time_group = self.new_time_group,
			)


	def test_add_time_group_with_wrong_type(self):
		"""
			Generar un error por enviar un valor muy corto( o largo) para 'type'
		"""

		test_cases = [
			{
				"type" : faker.pystr(
					max_chars = models.MIN_LENGTH_TYPEGROUP_TYPE - 1)
			},
			{
				"type" : faker.pystr(
					max_chars = models.MAX_LENGTH_TYPEGROUP_TYPE + 1)
			}
		]

		for case in test_cases:
			with self.subTest(case = case):
				self.new_time_group.update({"type": case["type"]})

				with self.assertRaises(ValidationError):
					commands.add_time_group(
						time_group = self.new_time_group,
					)


	def test_add_time_group_with_wrong_dasyweek(self):
		"""
			Generar error por enviar valores incorrectos en 'daysweek'
		"""
		daysweek = faker.random_elements(
			length=3, 
			unique=True,
			elements=[2, 6, 7, 8, 9, 10], 
		)

		self.new_time_group.update({"daysweek": daysweek})

		error_message = TimeGroupErrorsMessages.INVALID_DAYSWEEK

		with self.assertRaisesMessage(ValidationError, error_message):
			commands.add_time_group(
				time_group = self.new_time_group,
			)


class CommandAddOfficeHourTest(CommandOfficeHourTest):
	
	def test_add_office_hour(self):
		"""
			Validar crear un 'OfficeHour'
		"""

		description = faker.text(
			max_nb_chars = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D
		)

		office_hour = commands.add_office_hour(
			school_id = self.school.id,
			description = description
		)

		self.assertTrue(office_hour)
		self.assertTrue(office_hour.id)
		self.assertEqual(office_hour.school.id, self.school.id)
		self.assertEqual(office_hour.interval_description, description)


	def test_add_office_hour_with_wrong_description(self):
		"""
			Generar un error por enviar un valor muy corto( o largo) para 'interval_description'
		"""

		test_cases = [
			{
				"value": faker.pystr(
					max_chars = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D + 1
				),
				"expected": {
					"error_message": OfficeHourErrorsMessages.MAX_LEN
				}
			},
			{
				"value": faker.pystr(
					max_chars = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D - 1
				),
				"expected": {
					"error_message": OfficeHourErrorsMessages.MIN_LEN
				}
			}
		]

		for case in test_cases:
			with self.subTest(case = case):
				error_message = case["expected"]["error_message"]
				with self.assertRaisesMessage(ValueError, error_message) as cm:
					office_hour = commands.add_office_hour(
						school_id = self.school.id,
						description = case["value"]
					)


class CommandCreateOfficeHourTest(CommandOfficeHourTest):
	def setUp(self):
		super().setUp()

		self.daysweek = create_daysweek()

		self.new_office_hour = {
			"description": faker.text(
				max_nb_chars = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D
			),
			"time_group": {
				"type": faker.text(
					max_nb_chars = models.MAX_LENGTH_TYPEGROUP_TYPE
				),
				"opening_time": datetime.time(7, 30),
				"closing_time": datetime.time(14, 30),
				"active": random.choice([True, False]),
				"overview": faker.paragraph(),
				"daysweek": faker.random_elements(
					length=4, 
					unique=True,
					elements=[1,2,3,4,5], 
				)
			}
		}


	def test_create_office_hour(self):
		"""
			Validar crear un 'OfficeHour'
		"""

		command = commands.create_office_hour(
			school_id = self.school.id,
			office_hour = self.new_office_hour
		)

		command_status = command.status
		command_query = command.query
		command_errors = command.errors

		self.assertTrue(command_status)
		self.assertTrue(command_query)
		self.assertIsNone(command_errors)

		self.assertTrue(command_query.id)
		self.assertEqual(
			command_query.interval_description, 
			self.new_office_hour["description"]
		)
		self.assertEqual(
			command_query.time_group.type, 
			self.new_office_hour["time_group"]["type"]
		)
		self.assertEqual(
			command_query.time_group.active, 
			self.new_office_hour["time_group"]["active"]
		)
		self.assertEqual(
			command_query.time_group.overview, 
			self.new_office_hour["time_group"]["overview"]
		)

		self.assertGreaterEqual(command_query.time_group.daysweek.count(), 1)

	def test_create_office_hour_without_daysweek(self):
		"""
			Validar crear un 'OfficeHour' sin 'daysweek'
		"""
		self.new_office_hour["time_group"].pop("daysweek")

		command = commands.create_office_hour(
			school_id = self.school.id,
			office_hour = self.new_office_hour
		)

		command_status = command.status
		command_query = command.query
		command_errors = command.errors

		self.assertTrue(command_status)
		self.assertTrue(command_query)
		self.assertIsNone(command_errors)

		self.assertTrue(command_query.id)
		self.assertEqual(
			command_query.interval_description, 
			self.new_office_hour["description"]
		)
		self.assertEqual(
			command_query.time_group.type, 
			self.new_office_hour["time_group"]["type"]
		)
		self.assertEqual(
			command_query.time_group.active, 
			self.new_office_hour["time_group"]["active"]
		)
		self.assertEqual(
			command_query.time_group.overview, 
			self.new_office_hour["time_group"]["overview"]
		)

		self.assertLess(
			command_query.time_group.daysweek.count(), 1
		)

	def test_create_office_hour_without_overview(self):
		"""
			Validar crear un 'OfficeHour' sin 'overview'
		"""
		self.new_office_hour["time_group"].pop("overview")

		command = commands.create_office_hour(
			school_id = self.school.id,
			office_hour = self.new_office_hour
		)

		command_status = command.status
		command_query = command.query
		command_errors = command.errors

		self.assertTrue(command_status)
		self.assertTrue(command_query)
		self.assertIsNone(command_errors)

		self.assertTrue(command_query.id)
		self.assertEqual(
			command_query.time_group.active, 
			self.new_office_hour["time_group"]["active"]
		)
		self.assertEqual(
			command_query.interval_description, 
			self.new_office_hour["description"]
		)
		self.assertEqual(
			command_query.time_group.type, 
			self.new_office_hour["time_group"]["type"]
		)
		self.assertIsNone(
			command_query.time_group.overview
		)
		self.assertGreaterEqual(command_query.time_group.daysweek.count(), 1)

	def test_create_office_hour_without_active(self):
		"""
			Validar crear un 'OfficeHour' sin 'active'
		"""
		self.new_office_hour["time_group"].pop("active")

		command = commands.create_office_hour(
			school_id = self.school.id,
			office_hour = self.new_office_hour
		)

		command_status = command.status
		command_query = command.query
		command_errors = command.errors

		self.assertTrue(command_status)
		self.assertTrue(command_query)
		self.assertIsNone(command_errors)

		self.assertTrue(command_query.id)
		self.assertTrue(
			command_query.time_group.active
		)
		self.assertEqual(
			command_query.interval_description, 
			self.new_office_hour["description"]
		)
		self.assertEqual(
			command_query.time_group.type, 
			self.new_office_hour["time_group"]["type"]
		)
		self.assertEqual(
			command_query.time_group.overview, 
			self.new_office_hour["time_group"]["overview"]
		)
		self.assertGreaterEqual(command_query.time_group.daysweek.count(), 1)

	def test_create_office_hour_with_wrong_time(self):
		"""
			Generar error por definir 'closing_time' > 'opening_time'
		"""

		self.new_office_hour["time_group"].update({
			"closing_time":  datetime.time(7, 30),
			"opening_time": datetime.time(17, 30)
		})

		error_message = TimeGroupErrorsMessages.WRONG_TIME
		
		command = commands.create_office_hour(
			school_id = self.school.id,
			office_hour = self.new_office_hour
		)

		command_status = command.status
		command_query = command.query
		command_errors = command.errors

		self.assertFalse(command_status)
		self.assertIsNone(command_query)
		self.assertTrue(command_errors)
		self.assertEqual(command_errors[0].message, error_message)

	def test_create_office_hour_with_wrong_daysweek(self):
		"""
			Generar error por definir un valor [ x < 1 | x > 5]
		"""

		self.new_office_hour["time_group"].update({
			"daysweek": faker.random_elements(
				length=4, 
				unique=True,
				elements=[6,7,2,1,9,8,10], 
			)
		})

		error_message = TimeGroupErrorsMessages.INVALID_DAYSWEEK

		command = commands.create_office_hour(
			school_id = self.school.id,
			office_hour = self.new_office_hour
		)

		command_status = command.status
		command_query = command.query
		command_errors = command.errors

		self.assertFalse(command_status)
		self.assertIsNone(command_query)
		self.assertTrue(command_errors)
		self.assertEqual(command_errors[0].message , error_message)

	def test_create_office_hour_with_wrong_type(self):
		"""
			Generar error por definir un valor para 'type' muy corto (o muy largo)
		"""

		test_cases = [
			{
				"value": faker.pystr(
					max_chars = models.MIN_LENGTH_TYPEGROUP_TYPE - 1 
				),
				"expected": TimeGroupErrorsMessages.MIN_LEN,
			},
			{
				"value": faker.pystr(
					max_chars = models.MAX_LENGTH_TYPEGROUP_TYPE + 1 
				),
				"expected": TimeGroupErrorsMessages.MAX_LEN,
			}
		]

		for case in test_cases:
			with self.subTest(case = case):
				self.new_office_hour["time_group"].update({
					"type": case["value"]
				})
				
				error_message = case["expected"]

				command = commands.create_office_hour(
					school_id = self.school.id,
					office_hour = self.new_office_hour
				)

				command_status = command.status
				command_query = command.query
				command_errors = command.errors

				self.assertFalse(command_status)
				self.assertIsNone(command_query)
				self.assertTrue(command_errors)
				self.assertEqual(command_errors[0].message, error_message)

	def test_create_office_hour_with_wrong_description(self):
		"""
			Generar un error po definir un valor para 'description' muy corto (o muy largo)
		"""
		test_cases = [
			{
				"value": faker.pystr(
					max_chars = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D - 1 
				),
				"expected": OfficeHourErrorsMessages.MIN_LEN,
			},
			{
				"value": faker.pystr(
					max_chars = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D + 1 
				),
				"expected": OfficeHourErrorsMessages.MAX_LEN,
			}
		]

		for case in test_cases:
			with self.subTest(case = case):
				self.new_office_hour.update({"description": case["value"]})
				
				error_message = case["expected"]

				command = commands.create_office_hour(
					school_id = self.school.id,
					office_hour = self.new_office_hour
				)

				command_status = command.status
				command_query = command.query
				command_errors = command.errors

				self.assertFalse(command_status)
				self.assertIsNone(command_query)
				self.assertTrue(command_errors)
				self.assertEqual(command_errors[0].message, error_message)
