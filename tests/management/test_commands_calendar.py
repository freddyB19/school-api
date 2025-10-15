import unittest

from rest_framework import exceptions

from apps.school import models
from apps.management.apiv1.school import serializers

from tests import faker

from tests.school.utils import create_calendar
from .utils import testcases, testcases_data



class CommandCreateCalendarTest(testcases.CommandCalendarTestCase):
	def setUp(self):
		super().setUp()

		self.add_calendar = {
			"title": faker.text(max_nb_chars = models.MAX_LENGTH_CALENDAR_TITLE),
			"description": faker.paragraph(),
			"date": faker.date_this_year()
		}

	def test_create_calendar(self):
		"""
			Validar crear una fecha en el calendario
		"""

		serializer = serializers.MSchoolCalendarRequest(
			data = self.add_calendar,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		calendar = serializer.save()

		self.assertTrue(calendar.id)
		self.assertEqual(calendar.title, self.add_calendar["title"])
		self.assertEqual(calendar.description, self.add_calendar["description"])
		self.assertEqual(calendar.date, self.add_calendar["date"])

	def test_create_calendar_without_description(self):
		"""
			Validar crear una fecha en el calendario sin enviar descripción
		"""
		self.add_calendar.pop("description")

		serializer = serializers.MSchoolCalendarRequest(
			data = self.add_calendar,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		calendar = serializer.save()

		self.assertTrue(calendar.id)
		self.assertEqual(calendar.title, self.add_calendar["title"])
		self.assertIsNone(calendar.description)
		self.assertEqual(calendar.date, self.add_calendar["date"])


	def test_create_calendar_with_wrong_data(self):
		"""
			Generar error por crear una fecha en el calendario con datos invalidos
		"""
		
		test_cases = testcases_data.CREATE_CALENDAR_WITH_WRONG_DATA

		for case in test_cases:
			with self.subTest(case = case):

				serializer = serializers.MSchoolCalendarRequest(
					data = case,
					context = {"pk": self.school.id}
				)
				
				with self.assertRaises(exceptions.ValidationError):
					serializer.is_valid(raise_exception = True)


	def test_create_calendar_with_does_not_exist_school(self):
		"""
			Generar error por crear una fecha en el calendario con el ID de una escuela que no existe
		"""
		wrong_id = faker.random_int(min = self.school.id + 1)

		serializer = serializers.MSchoolCalendarRequest(
			data = self.add_calendar,
			context = {"pk": wrong_id}
		)

		serializer.is_valid(raise_exception = True)

		with self.assertRaises(exceptions.ValidationError):
			calendar = serializer.save()
	
	def test_create_calendar_already_exists(self):
		"""
			Generar un error por una fecha en el calendario con datos ya registrados
		"""

		title = faker.text(max_nb_chars = models.MAX_LENGTH_CALENDAR_TITLE)
		date = faker.date_this_year()

		create_calendar(title = title, date = date, school = self.school)

		self.add_calendar.update({"title": title, "date": date})

		serializer = serializers.MSchoolCalendarRequest(
			data = self.add_calendar,
			context = {"pk": self.school.id}
		)
		
		with self.assertRaises(exceptions.ValidationError):

			serializer.is_valid(raise_exception = True)