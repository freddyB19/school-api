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


CREATE_CALENDAR_WITH_WRONG_DATA = [
	{
		"title": faker.pystr(
			max_chars = school_models.MAX_LENGTH_CALENDAR_TITLE + 1
		),
		"date": faker.date_this_year()
	},
	{
		"title": faker.pystr(
			max_chars = school_models.MIN_LENGTH_CALENDAR_TITLE - 1
		),
		"date": faker.date_this_year()
	},
]


UPDATE_SOCIALMEDIA_WITH_WRONG_DATA = [
	{
		"profile": faker.url()[:4]
	}
]


coordinate = faker.local_latlng(country_code = 'VE')

CREATE_COORDINATE_WITH_WRONG_DATA = [
	{
		"title": faker.pystr(
			max_chars = school_models.MAX_LENGTH_COORDINATE_TITLE + 1
		),
		"latitude": coordinate[0],
		"longitude": coordinate[1]
	},
	{
		"title": faker.pystr(
			max_chars = school_models.MIN_LENGTH_COORDINATE_TITLE - 1
		),
		"latitude": coordinate[0],
		"longitude": coordinate[1]
	}
]

CREATE_STAFF_WITH_WRONG_DATA = [
	{
		"name": faker.pystr(
			max_chars = school_models.MAX_LENGTH_SCHOOSTAFF_NAME + 1
		)
	},
	{
		"name": faker.pystr(
			max_chars = school_models.MIN_LENGTH_SCHOOSTAFF_NAME - 1
		)
	},
	{
		"name": faker.first_name(),
		"occupation": faker.job()
	}
]


CREATE_GRADE_WITH_WRONG_DATA = [
	{ # Validar nombre muy corto
		"name": faker.pystr(
			max_chars = school_models.MIN_LENGTH_GRADE_NAME - 1
		),
		"level": faker.random_int(
			min = school_models.MIN_LENGTH_GRADE_LEVEL, 
			max = school_models.MAX_LENGTH_GRADE_LEVEL
		),
		"section": faker.random_letter()
	},
	{ # Validar nombre muy largo
		"name": faker.pystr(
			max_chars = school_models.MAX_LENGTH_GRADE_NAME + 1
		),
		"level": faker.random_int(
			min = school_models.MIN_LENGTH_GRADE_LEVEL, 
			max = school_models.MAX_LENGTH_GRADE_LEVEL
		),
		"section": faker.random_letter()
	},
	{ # Validar nivel con valor muy bajo
		"name": faker.text(max_nb_chars = school_models.MAX_LENGTH_GRADE_NAME),
		"level": faker.random_int(max = school_models.MIN_LENGTH_GRADE_LEVEL - 1),
		"section": faker.random_letter()
	},
	{ # Validar nivel con valor muy alto
		"name": faker.text(max_nb_chars = school_models.MAX_LENGTH_GRADE_NAME),
		"level": faker.random_int(min = school_models.MAX_LENGTH_GRADE_LEVEL + 1),
		"section": faker.random_letter()
	},
	{ # Validar sección muy larga
		"name": faker.text(max_nb_chars = school_models.MAX_LENGTH_GRADE_NAME),
		"level": faker.random_int(
			min = school_models.MIN_LENGTH_GRADE_LEVEL, 
			max = school_models.MAX_LENGTH_GRADE_LEVEL
		),
		"section": faker.pystr(
			max_chars = school_models.MAX_LENGTH_GRADE_SECTION + 1
		)
	}
]


CREATE_REPOSITORY_WITH_WRONG_DATA = [
	{"name_project": faker.pystr(
		max_chars = school_models.MIN_LENGTH_REPOSITORY_NAME_PROJECT - 1)
	},
	{"name_project": faker.pystr(
		max_chars = school_models.MAX_LENGTH_REPOSITORY_NAME_PROJECT + 1)
	},
	{"description": faker.paragraph()}
]


UPDATE_REPOSITORY_WITH_WRONG_DATA = [
	{"name_project": faker.pystr(
		max_chars = school_models.MIN_LENGTH_REPOSITORY_NAME_PROJECT - 1)
	},
	{"name_project": faker.pystr(
		max_chars = school_models.MAX_LENGTH_REPOSITORY_NAME_PROJECT + 1)
	}
]
