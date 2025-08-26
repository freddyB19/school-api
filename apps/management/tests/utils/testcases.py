from .utils import get_long_string

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