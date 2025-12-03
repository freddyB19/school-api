import unittest

from rest_framework import exceptions

from apps.school import models
from apps.management.apiv1.school import serializers

from tests import faker

from .utils import testcases, testcases_data
from tests.school.utils import create_educational_stage, create_grade


class CommandCreateGradeTest(testcases.BasicCommandTestCase):
	def setUp(self):
		super().setUp()

		self.stage = create_educational_stage()

		self.add_grade = {
			"name": faker.text( max_nb_chars = models.MAX_LENGTH_GRADE_NAME),
			"level": faker.random_int(
				min = models.MIN_LENGTH_GRADE_LEVEL, 
				max = models.MAX_LENGTH_GRADE_LEVEL
			),
			"section": faker.random_letter(),
			"description": faker.paragraph(),
			"stage_id": self.stage.id
		}

	def test_create_grade(self):
		"""
			Validar crear una grado de una escuela
		"""
		serializer = serializers.MSchoolGradeRequest(
			data = self.add_grade,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		grade = serializer.save()

		self.assertTrue(grade)
		self.assertEqual(grade.name, self.add_grade["name"])
		self.assertEqual(grade.level, self.add_grade["level"])
		self.assertEqual(grade.section, self.add_grade["section"])
		self.assertEqual(grade.description, self.add_grade["description"])
		self.assertEqual(grade.stage.id, self.add_grade["stage_id"])

	def test_create_grade_without_section(self):
		"""
			Validar crear una grado de una escuela sin definir la 'sección'
		"""
		self.add_grade.pop("section")

		serializer = serializers.MSchoolGradeRequest(
			data = self.add_grade,
			context = {"pk": self.school.id}
		)

		serializer.is_valid(raise_exception = True)

		grade = serializer.save()

		self.assertTrue(grade)
		self.assertIsNone(grade.section)
		self.assertEqual(grade.name, self.add_grade["name"])
		self.assertEqual(grade.level, self.add_grade["level"])
		self.assertEqual(grade.description, self.add_grade["description"])
		self.assertEqual(grade.stage.id, self.add_grade["stage_id"])


	def test_create_grade_with_wrong_data(self):
		"""
			Generar un error por enviar datos invalidos
		"""

		test_case = testcases_data.CREATE_GRADE_WITH_WRONG_DATA

		for case in test_case:
			with self.subTest(case = case):
				case.update({"stage_id": self.stage.id})
				
				serializer = serializers.MSchoolGradeRequest(
					data = case,
					context = {"pk": self.school.id}
				)

				with self.assertRaises(exceptions.ValidationError):
					serializer.is_valid(raise_exception = True)

	def test_create_grade_already_exist(self):
		"""
			Generar un error por enviar datos ya registrados
		"""
		grade = create_grade(school = self.school)

		self.add_grade.update({
			"stage_id": grade.stage.id,
			"level": grade.level,
			"section": grade.section
		})

		serializer = serializers.MSchoolGradeRequest(
			data = self.add_grade,
			context = {"pk": self.school.id}
		)

		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)

	def test_create_grade_with_does_not_exit_school(self):
		"""
			Generar un error por pasar el ID de una escuela que no existe
		"""
		wrong_school_id = faker.random_int(min = self.school.id + 1)
		
		serializer = serializers.MSchoolGradeRequest(
			data = self.add_grade,
			context = {"pk": wrong_school_id}
		)

		serializer.is_valid(raise_exception = True)

		with self.assertRaises(exceptions.ValidationError):
			grade = serializer.save()


	def test_create_grade_with_does_not_exit_stage(self):
		"""
			Generar un error por pasar el ID de una 'Etapa educativa' que no existe
		"""
		self.add_grade.update({
			"stage_id": faker.random_int(min = self.stage.id + 1
		)})
		
		serializer = serializers.MSchoolGradeRequest(
			data = self.add_grade,
			context = {"pk": self.school.id}
		)

		with self.assertRaises(exceptions.ValidationError):
			serializer.is_valid(raise_exception = True)
