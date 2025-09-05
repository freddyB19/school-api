from django.test import TestCase

from pydantic import ValidationError

from apps.utils.result_commands import (
	ResultCommand,
	WITHOUT_ERRORS,
	WITHOUT_ERROR_CODE,
	WITHOUT_ERROR_CODE_AND_ERRORS
)

class ResultCommandTest(TestCase):

	def test_validate_without_errors(self):
		"""
			Retornar instancia de 'ResultCommand' sin generar algún error
		"""
		context = {
			"query": 12,
			"status": True
		}

		command = ResultCommand(**context)

		self.assertTrue(command.status)
		self.assertEqual(command.query, context["query"])

		self.assertIsNone(command.errors)
		self.assertIsNone(command.error_code)


	def test_validate_error_by_error_code_property(self):
		"""
			Generar un error por definir 'errors' sin 'error_code'
		"""

		with self.assertRaisesMessage(ValidationError, WITHOUT_ERROR_CODE):
			ResultCommand(status = False, errors = [{"message": "Error..."}])

	def test_validate_error_by_errors_property(self):
		"""
			Generar un error por definir 'error_code' sin 'errors'
		"""

		with self.assertRaisesMessage(ValidationError, WITHOUT_ERRORS):
			ResultCommand(status = False, error_code = 400)


	def test_validate_error_invalid_error_code(self):
		"""
			Generar un error por definir un código de error invalido
			El código de error debe ser un número entre  >= 400 and < 600 
		"""
		error_code = 700

		with self.assertRaises(ValidationError):
			ResultCommand(status = False, error_code = error_code, errors = [{"message": "Error..."}])


	def test_validate_error_by_status_false_without_errors_and_error_code(self):
		"""
			Generar un error por definir 'status=False' sin definir 'errors' and "error_code"
		"""
		with self.assertRaisesMessage(ValidationError, WITHOUT_ERROR_CODE_AND_ERRORS):
			ResultCommand(status = False)

