import unittest

from rest_framework import exceptions

from apps.school import models
from apps.management.apiv1.school import serializers

from tests import faker

from tests.school.utils import create_coordinate
from .utils import testcases, testcases_data


class CommandCreateCoordinateTest(testcases.BasicCommandTestCase):
	def setUp(self):
		super().setUp()

		coordinate = faker.local_latlng(country_code = 'VE')

		self.add_coordinate = {
			"title": faker.text(max_nb_chars = models.MAX_LENGTH_COORDINATE_TITLE),
			"latitude": coordinate[0],
			"longitude": coordinate[1]
		}

	def test_create_coordinate(self):
		"""
			Validar agregar una coordenada
		"""
		serializer = serializers.MSchoolCoordinateRequest(
			data = self.add_coordinate,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		coordinate = serializer.save()

		self.assertTrue(coordinate.id)
		self.assertEqual(coordinate.title, self.add_coordinate["title"])


	def test_create_coordinate_with_wrong_data(self):
		"""
			Generar error por agregar una coordenada con datos invalidos
		"""

		test_case = testcases_data.CREATE_COORDINATE_WITH_WRONG_DATA

		for case in test_case:
			with self.subTest(case = case):
				serializer = serializers.MSchoolCoordinateRequest(
					data = case,
					context = {"pk": self.school.id}
				)

				with self.assertRaises(exceptions.ValidationError):
					serializer.is_valid(raise_exception = True)


	def test_create_coordinate_with_does_not_exist_school(self):
		"""
			Generar error por agregar una coordenada con el ID de una escuela que no existe
		"""

		wrong_school_id = faker.random_int(min = self.school.id + 1)
		
		serializer = serializers.MSchoolCoordinateRequest(
			data = self.add_coordinate,
			context = {"pk": wrong_school_id}
		)

		serializer.is_valid(raise_exception = True)

		with self.assertRaises(exceptions.ValidationError):
			serializer.save()

	def test_create_coordinate_already_exists(self):
		"""
			Generar un error por una coordenada con datos ya registrados
		"""
		coordinate = create_coordinate(school = self.school)

		self.add_coordinate.update({
				"title": coordinate.title,
				"latitude": coordinate.latitude,
				"longitude": coordinate.longitude
			})

		serializer = serializers.MSchoolCoordinateRequest(
			data = self.add_coordinate,
			context = {"pk": self.school.id}
		)

		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)