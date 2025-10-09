"""
	Funciones (commands) que forman parte de la creación 
	de un objeto 'OfficeHour'
"""
import random, datetime

from tests import faker

from pydantic import ValidationError

from apps.school import models

from apps.management.commands import commands
from apps.management.commands.utils.errors_messages import (
	TimeGroupErrorsMessages,
	OfficeHourErrorsMessages
)
from .utils import testcases

from tests.school.utils.utils import create_daysweek, create_time_group

class CommandAddTimeGroupTest(testcases.CommandTimeGroupTestCase):

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

	def test_add_time_group_with_wrong_time(self):
		"""
			Generar un error por definir 'closing_time' <= 'opening_time'
		"""
		error_message = TimeGroupErrorsMessages.WRONG_TIME

		# 'closing_time' < opening_time
		self.new_time_group.update({
			"closing_time": datetime.time(7,00),
			"opening_time": datetime.time(12,00),
		})

		with self.assertRaisesMessage(ValidationError, error_message):
			commands.add_time_group(
				time_group = self.new_time_group,
			)
		
		# 'closing_time' == opening_time
		self.new_time_group.update({
			"closing_time": datetime.time(7,00),
			"opening_time": datetime.time(7,00),
		})
		
		with self.assertRaisesMessage(ValidationError, error_message):
			commands.add_time_group(
				time_group = self.new_time_group,
			)


class CommandGetOrCreateTimeGroupTest(testcases.CommandGetOrCreateTimeGroupTestCase):
	def test_get_time_group(self):
		"""
			Validar que retorna un 'time_group' por su id
		"""
		return_time_group = commands.get_or_create_time_group(
			time_group = {"id": self.time_group.id}
		)

		self.assertTrue(return_time_group)
		self.assertEqual(return_time_group.id, self.time_group.id)


	def test_get_none_if_does_not_exist(self):
		"""
			Validar que retorna un 'None' por un id que no existe
		"""
		wrong_id = faker.random_int(min = self.time_group.id + 1)

		return_time_group = commands.get_or_create_time_group(
			time_group = {"id": wrong_id}
		)

		self.assertIsNone(return_time_group)

	def test_create_time_group(self):
		"""
			Validar que crea un nuevo 'time_group'
		"""

		new_time_group = {
			"type": faker.text(max_nb_chars = models.MAX_LENGTH_TYPEGROUP_TYPE),
			"opening_time": datetime.time(6, 50),
			"closing_time": datetime.time(17, 50)
		}

		time_group = commands.get_or_create_time_group(
			time_group = new_time_group
		)

		self.assertTrue(time_group)
		self.assertNotEqual(time_group.id, self.time_group.id)
		self.assertEqual(time_group.type, new_time_group['type'])
		self.assertIsInstance(time_group, models.TimeGroup)

class CommandAddOfficeHourTest(testcases.CommandOfficeHourTestCase):
	
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


class CommandCreateOfficeHourTest(testcases.CommandOfficeHourTestCase):
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
			Generar error por definir 'closing_time' <= 'opening_time'
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
			Generar error por definir un valor [ x < 1 | x > 5] para daysweek
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


	def test_create_office_hour_with_time_group_by_id(self):
		"""
			Validar crear un horario de oficina con un 'time_group' ya existente
		"""
		time_group = create_time_group()

		self.new_office_hour.update({"time_group": {"id": time_group.id}})

		command = commands.create_office_hour(
			school_id = self.school.id,
			office_hour = self.new_office_hour
		)

		command_query = command.query
		command_status = command.status
		command_errors = command.errors

		self.assertTrue(command_query)
		self.assertTrue(command_status)
		self.assertIsNone(command_errors)

		self.assertEqual(command_query.time_group.id, time_group.id)
		self.assertEqual(
			command_query.interval_description, 
			self.new_office_hour['description']
		)

	def test_create_office_hour_with_does_not_exist_time_group(self):
		"""
			Generar un error por crear un horario de oficina con un 'time_group' que no existe
		"""
		wrong_id = faker.random_int(min = 1)
		error_message = TimeGroupErrorsMessages.DOES_NOT_EXIST

		self.new_office_hour.update({"time_group": {"id": wrong_id}})

		command = commands.create_office_hour(
			school_id = self.school.id,
			office_hour = self.new_office_hour
		)

		command_query = command.query
		command_status = command.status
		command_errors = command.errors

		self.assertIsNone(command_query)
		self.assertFalse(command_status)
		self.assertTrue(command_errors)

		self.assertEqual(command_errors[0].message, error_message)



