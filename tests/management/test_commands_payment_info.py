"""
	Funciones (commands) que forman parte de la creación 
	de un objeto 'PaymentInfoMedia'
"""

from pydantic import ValidationError

from rest_framework import exceptions

from apps.school import models
from apps.management.commands import commands
from apps.management.apiv1.school import serializers

from tests import faker
from .utils import testcases, list_upload_files, create_list_files

class CommandAddPaymentInfoMediaTest(testcases.BasicCommandTestCase):

	def test_add_payment_info_media(self):
		"""
			Validar agregar archivos sobre 'payment-info-media' 
		"""

		total_files = 3

		command = commands.add_payment_info_media(
			media = list_upload_files(size = total_files, type_file = "image")
		)

		result = command.query
		status = command.status

		self.assertTrue(status)

		self.assertIsInstance(result[0], models.PaymentInfoMedia)

		total_created = len(result)

		self.assertEqual(total_created, total_files)

	def test_add_payment_info_media_with_wrong_data(self):
		"""
			Generar un error por enviar archivos invalidos
		"""

		total_files = 3

		with self.assertRaises(ValidationError):
			command = commands.add_payment_info_media(
				media = create_list_files(size = total_files, type_file = "image")
			)


class CommandsCreatePaymentInfoTest(testcases.BasicCommandTestCase):

    def setUp(self):
        super().setUp()

        self.add_payment_info = {
            "media": list_upload_files(size = 1, type_file = "image"),
            "description": faker.paragraph()
        }


    def test_command_create_payment_info(self):
        """
            Validar crear un registro para la información sobre pagos
        """

        serializer = serializers.MSchoolPaymentInfoRequest(
            data = self.add_payment_info,
            context = {"pk": self.school.id}
        )

        serializer.is_valid(raise_exception = True)
        payment_info = serializer.save()

        self.assertTrue(payment_info)
        self.assertTrue(payment_info.id)
        self.assertEqual(payment_info.school_id, self.school.id)
        self.assertEqual(payment_info.description, self.add_payment_info["description"])

    def test_command_create_payment_info_without_description(self):
        """
            Validar crear un registro para la información sobre pagos (sin descripción)
        """
        self.add_payment_info.pop("description")

        serializer = serializers.MSchoolPaymentInfoRequest(
            data = self.add_payment_info,
            context = {"pk": self.school.id}
        )

        serializer.is_valid(raise_exception = True)
        payment_info = serializer.save()

        self.assertTrue(payment_info)
        self.assertTrue(payment_info.id)
        self.assertEqual(payment_info.school_id, self.school.id)
        self.assertIsNone(payment_info.description)

    def test_command_create_payment_info_without_media(self):
        """
            Generar un error por intentar crear un registro sin "media" (imagen)
        """

        self.add_payment_info.pop("media")

        serializer = serializers.MSchoolPaymentInfoRequest(
            data = self.add_payment_info,
            context = {"pk": self.school.id}
        )

        with self.assertRaises(exceptions.ValidationError):
            serializer.is_valid(raise_exception = True)
