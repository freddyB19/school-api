from apps.school import models

from rest_framework import serializers

ERROR_FIELD = lambda field, type, simbol, value: f"El campo '{field}' es muy {type}, debe ser {simbol} a {value}" 

MAX_LENGTH_ADDRESS = 100
MIN_LENGTH_ADDRESS = 10

MAX_LENGTH_NAME = 50
MIN_LENGTH_NAME = 5


MIN_LENGTH_FIELDS = 10

class SchoolUpdateRequest(serializers.ModelSerializer):
	class Meta:
		model = models.School
		fields = [
			"id",
			"subdomain",
			"name",
			"address",
			"mission",
			"vision",
			"history",
		]

		read_only_fields = ["id", "subdomain"]

		extra_kwargs = {
			"name": {
				"max_length": MAX_LENGTH_NAME,
				"min_length": MIN_LENGTH_NAME,
				"error_messages": {
					"max_length": ERROR_FIELD(
						field = "nombre", 
						type = "largo",
						simbol = "menor o igual",
						value = MAX_LENGTH_NAME
					),
					"min_length": ERROR_FIELD(
						field = "nombre", 
						type = "corto",
						simbol = "mayor o igual",
						value = MIN_LENGTH_NAME
					)
				}
			},
			"address": {
				"max_length": MAX_LENGTH_ADDRESS,
				"min_length": MIN_LENGTH_ADDRESS,
				"error_messages": {
					"max_length": ERROR_FIELD(
						field = "dirección", 
						type = "largo",
						simbol = "menor o igual",
						value = MAX_LENGTH_ADDRESS
					),
					"min_length": ERROR_FIELD(
						field = "misión",
						type = "corto",
						simbol = "mayor o igual",
						value = MIN_LENGTH_ADDRESS
					)
				}
			},
			"mission": {
				"min_length": MIN_LENGTH_FIELDS,
				"error_messages": {
					"min_length": ERROR_FIELD(
						field = "misión", 
						type = "corto",
						simbol = "mayor o igual",
						value = MIN_LENGTH_FIELDS
					)
				}
			},
			"vision": {
				"min_length": MIN_LENGTH_FIELDS,
				"error_messages": {
					"min_length": ERROR_FIELD(
						field = "visión", 
						type = "corto",
						simbol = "mayor o igual",
						value = MIN_LENGTH_FIELDS
					)
				}
			},
			"history": {
				"min_length": MIN_LENGTH_FIELDS,
				"error_messages": {
					"min_length": ERROR_FIELD(
						field = "historia", 
						type = "corto",
						simbol = "mayor o igual",
						value = MIN_LENGTH_FIELDS
					)
				}
			},
		}


class SchoolUpdateLogoRequest(serializers.Serializer):
	logo = serializers.ImageField(required = False, max_length = 20)
	