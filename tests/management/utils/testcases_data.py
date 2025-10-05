from apps.school import models as school_models

from tests import faker

from .utils import set_daysweek, get_long_string

UPDATE_SCHOOL_WITH_WRONG_DATA = [
	{
		"update": {
			"name": faker.pystr(max_chars = school_models.MIN_LENGTH_SCHOOL_NAME - 1)
		},
		"expect": {
			"code": 400,
			"field": "name",
		}
	},
	{
		"update": {
			"name": get_long_string()
		},
		"expect": {
			"code": 400,
			"field": "name",
		}
	},
	{
		"update": {
			"address": get_long_string()
		},
		"expect": {
			"code": 400,
			"field": "address",
		}
	},
	{
		"update": {
			"address": faker.pystr(max_chars = school_models.MIN_LENGTH_SCHOOL_ADDRESS - 1)
		},
		"expect": {
			"code": 400,
			"field": "address",
		}
	},
	{
		"update": {
			"mission":faker.pystr(max_chars = 4)
		},
		"expect": {
			"code": 400,
			"field": "mission",
		}
	},
	{
		"update": {
			"vision": faker.pystr(max_chars = 4)
		},
		"expect": {
			"code": 400,
			"field": "vision",
		}
	},
	{
		"update": {
			"history": faker.pystr(max_chars = 4)
		},
		"expect": {
			"code": 400,
			"field": "history",
		}
	},
]


UPDATE_OFFICEHOUR_WITH_WRONG_DATA = [
	{
		"description": faker.pystr(
			max_chars = school_models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D + 1,
		)
	},
	{
		"description": faker.pystr(
			max_chars = school_models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D - 1,
		)
	}
]
