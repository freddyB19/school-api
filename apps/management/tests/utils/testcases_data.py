from apps.school import models as school_models

from apps.management.tests import faker

from .utils import set_daysweek

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