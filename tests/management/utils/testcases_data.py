import datetime
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


UPDATE_TIMEGROUP_WITH_WRONG_DATA = [

	{
		"update": {
			"type": faker.pystr(
				max_chars = school_models.MAX_LENGTH_TYPEGROUP_TYPE + 1
			)
		}
	},
	{
		"update": {
			"daysweek": set_daysweek(days = [6,7,2,9,8,10,1], length = 3) 
		}
	},
	{
		"update": {
			"opening_time": datetime.time(15, 30),
			"closing_time": datetime.time(12, 10)
		}
	},
	{
		"update": {
			"opening_time": datetime.time(15, 30),
		}
	}
]