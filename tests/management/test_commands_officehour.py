"""
	Funciones (commands) que forman parte de la creación 
	de un objeto 'OfficeHour'
"""
import random, datetime

from tests import faker

from rest_framework import exceptions


from apps.school import models

from apps.management.apiv1.school import serializers
from .utils import testcases

from tests.school.utils.utils import (
	create_daysweek, 
	create_time_group, 
	create_officehour
)


class CommandCreateOfficeHourTest(testcases.BasicCommandTestCase):
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

		serializer = serializers.MSchoolOfficeHourRequest(
			data = self.new_office_hour,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		office_hour = serializer.save()

		self.assertTrue(office_hour.id)
		self.assertEqual(
			office_hour.interval_description, 
			self.new_office_hour["description"]
		)
		self.assertEqual(
			office_hour.time_group.type, 
			self.new_office_hour["time_group"]["type"]
		)
		self.assertEqual(
			office_hour.time_group.active, 
			self.new_office_hour["time_group"]["active"]
		)
		self.assertEqual(
			office_hour.time_group.overview, 
			self.new_office_hour["time_group"]["overview"]
		)

		self.assertGreaterEqual(office_hour.time_group.daysweek.count(), 1)

	def test_create_office_hour_without_daysweek(self):
		"""
			Validar crear un 'OfficeHour' sin 'daysweek'
		"""
		self.new_office_hour["time_group"].pop("daysweek")

		serializer = serializers.MSchoolOfficeHourRequest(
			data = self.new_office_hour,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		office_hour = serializer.save()


		self.assertTrue(office_hour.id)
		self.assertLess(
			office_hour.time_group.daysweek.count(), 1
		)
		self.assertEqual(
			office_hour.interval_description, 
			self.new_office_hour["description"]
		)
		self.assertEqual(
			office_hour.time_group.type, 
			self.new_office_hour["time_group"]["type"]
		)
		self.assertEqual(
			office_hour.time_group.active, 
			self.new_office_hour["time_group"]["active"]
		)
		self.assertEqual(
			office_hour.time_group.overview, 
			self.new_office_hour["time_group"]["overview"]
		)

	def test_create_office_hour_without_overview(self):
		"""
			Validar crear un 'OfficeHour' sin 'overview'
		"""
		self.new_office_hour["time_group"].pop("overview")

		serializer = serializers.MSchoolOfficeHourRequest(
			data = self.new_office_hour,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		office_hour = serializer.save()

		self.assertTrue(office_hour.id)
		self.assertIsNone(
			office_hour.time_group.overview
		)
		self.assertEqual(
			office_hour.time_group.active, 
			self.new_office_hour["time_group"]["active"]
		)
		self.assertEqual(
			office_hour.interval_description, 
			self.new_office_hour["description"]
		)
		self.assertEqual(
			office_hour.time_group.type, 
			self.new_office_hour["time_group"]["type"]
		)
		self.assertGreaterEqual(office_hour.time_group.daysweek.count(), 1)

	def test_create_office_hour_without_active(self):
		"""
			Validar crear un 'OfficeHour' sin 'active'
		"""
		self.new_office_hour["time_group"].pop("active")

		serializer = serializers.MSchoolOfficeHourRequest(
			data = self.new_office_hour,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		office_hour = serializer.save()

		self.assertTrue(office_hour.id)
		self.assertTrue(
			office_hour.time_group.active
		)
		self.assertEqual(
			office_hour.interval_description, 
			self.new_office_hour["description"]
		)
		self.assertEqual(
			office_hour.time_group.type, 
			self.new_office_hour["time_group"]["type"]
		)
		self.assertEqual(
			office_hour.time_group.overview, 
			self.new_office_hour["time_group"]["overview"]
		)
		self.assertGreaterEqual(office_hour.time_group.daysweek.count(), 1)

	def test_create_office_hour_with_wrong_time(self):
		"""
			Generar error por definir 'closing_time' <= 'opening_time'
		"""

		self.new_office_hour["time_group"].update({
			"closing_time":  datetime.time(7, 30),
			"opening_time": datetime.time(17, 30)
		})

		serializer = serializers.MSchoolOfficeHourRequest(
			data = self.new_office_hour,
			context = {"pk": self.school.id}
		)

		with self.assertRaises(exceptions.ValidationError):

			serializer.is_valid(raise_exception = True)

	def test_create_office_hour_with_wrong_daysweek(self):
		"""
			Generar error por definir un valor [ x < 1 | x > 5] para daysweek
		"""

		self.new_office_hour["time_group"].update({
			"daysweek": faker.random_elements(
				length=4, 
				unique=True,
				elements=[6,7,2,1,9,8,10], 
			)
		})

		serializer = serializers.MSchoolOfficeHourRequest(
			data = self.new_office_hour,
			context = {"pk": self.school.id}
		)

		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)

	def test_create_office_hour_with_wrong_type(self):
		"""
			Generar error por definir un valor para 'type' muy corto (o muy largo)
		"""

		test_cases = [
			{
				"value": faker.pystr(
					max_chars = models.MIN_LENGTH_TYPEGROUP_TYPE - 1 
				)
			},
			{
				"value": faker.pystr(
					max_chars = models.MAX_LENGTH_TYPEGROUP_TYPE + 1 
				)
			}
		]

		for case in test_cases:
			with self.subTest(case = case):
				self.new_office_hour["time_group"].update({
					"type": case["value"]
				})

				serializer = serializers.MSchoolOfficeHourRequest(
					data = self.new_office_hour,
					context = {"pk": self.school.id}
				)

				with self.assertRaises(exceptions.ValidationError):
					serializer.is_valid(raise_exception = True)
				
	def test_create_office_hour_with_wrong_description(self):
		"""
			Generar un error po definir un valor para 'description' muy corto (o muy largo)
		"""
		test_cases = [
			{
				"value": faker.pystr(
					max_chars = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D - 1 
				)
			},
			{
				"value": faker.pystr(
					max_chars = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D + 1 
				)
			}
		]

		for case in test_cases:
			with self.subTest(case = case):
				self.new_office_hour.update({"description": case["value"]})

				serializer = serializers.MSchoolOfficeHourRequest(
					data = self.new_office_hour,
					context = {"pk": self.school.id}
				)

				with self.assertRaises(exceptions.ValidationError):
					serializer.is_valid(raise_exception = True)


	def test_create_office_hour_with_time_group_by_id(self):
		"""
			Validar crear un horario de oficina con un 'time_group' ya existente
		"""
		# Creamos un 'time_group' asociado a la administración de nuestra escuela
		office_hour = create_officehour(
			school = self.school,
			time_group = create_time_group()
		)

		time_group_id = office_hour.time_group.id

		self.new_office_hour.pop("time_group")
		self.new_office_hour.update({"time_group_id": time_group_id})

		serializer = serializers.MSchoolOfficeHourRequest(
			data = self.new_office_hour,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		office_hour = serializer.save()

		self.assertEqual(office_hour.time_group.id, time_group_id)
		self.assertEqual(
			office_hour.interval_description, 
			self.new_office_hour['description']
		)

	def test_create_office_hour_with_does_not_exist_time_group(self):
		"""
			Generar un error por crear un horario de oficina con un 'time_group' que no existe
		"""
		wrong_id = faker.random_int(min = 1)

		self.new_office_hour.pop("time_group")
		self.new_office_hour.update({"time_group_id": wrong_id})

		serializer = serializers.MSchoolOfficeHourRequest(
			data = self.new_office_hour,
			context = {"pk": self.school.id}
		)

		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)
