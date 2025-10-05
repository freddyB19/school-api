from django.test import TestCase

from tests import faker

from . import utils

class DecoratorHandlerTestCase(TestCase):
	def setUp(self):
		self.user = {
			"name": faker.pystr(max_chars = utils.MAX_LEN_NAME + 1), 
			"age": faker.random_int(max = utils.AGE_GT - 1)
		}