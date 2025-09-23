from apps.school import models as school_models

from apps.management.tests import faker

from .utils import set_daysweek, get_long_string

UPDATE_SCHOOL_WITH_WRONG_DATA = [
	{
		"update": {
			"name": "Av12"
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
			"address": "short"
		},
		"expect": {
			"code": 400,
			"field": "address",
		}
	},
	{
		"update": {
			"mission": "short"
		},
		"expect": {
			"code": 400,
			"field": "mission",
		}
	},
	{
		"update": {
			"vision": "short"
		},
		"expect": {
			"code": 400,
			"field": "vision",
		}
	},
	{
		"update": {
			"history": "short"
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
