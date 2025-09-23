from typing import TypeVar
from datetime import datetime

from apps.school import models

from rest_framework import serializers

from apps.management.dtos import school as school_dto
from apps.school.apiv1 import serializers as school_serializer

ERROR_FIELD = lambda field, type, simbol, value: f"El campo '{field}' es muy {type}, debe ser {simbol} a {value}" 

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
				"max_length": models.MAX_LENGTH_SCHOOL_ADDRESS,
				"min_length": models.MIN_LENGTH_SCHOOL_ADDRESS,
				"error_messages": {
					"max_length": ERROR_FIELD(
						field = "nombre", 
						type = "largo",
						simbol = "menor o igual",
						value = models.MAX_LENGTH_SCHOOL_NAME
					),
					"min_length": ERROR_FIELD(
						field = "nombre", 
						type = "corto",
						simbol = "mayor o igual",
						value = models.MIN_LENGTH_SCHOOL_NAME
					)
				}
			},
			"address": {
				"max_length": models.MAX_LENGTH_SCHOOL_ADDRESS,
				"min_length": models.MIN_LENGTH_SCHOOL_ADDRESS,
				"error_messages": {
					"max_length": ERROR_FIELD(
						field = "dirección", 
						type = "largo",
						simbol = "menor o igual",
						value = models.MAX_LENGTH_SCHOOL_ADDRESS
					),
					"min_length": ERROR_FIELD(
						field = "misión",
						type = "corto",
						simbol = "mayor o igual",
						value = models.MIN_LENGTH_SCHOOL_ADDRESS
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
	logo = serializers.ImageField(max_length = 20)


MAX_LENGTH_IMAGE_NAME = 20

STATUS_INVALID_CHOICE = "La opción elegida es invalida"

class NewsRequest(serializers.ModelSerializer):
	media = serializers.ListField(
		required = False,
		child = serializers.ImageField(max_length = MAX_LENGTH_IMAGE_NAME), 
	)
	
	class Meta:
		model = models.News
		fields = [
			"title",
			"media",
			"status",
			"description",
		]

		extra_kwargs = {
			"title": {
				"max_length": models.MAX_LENGTH_NEWS_TITLE,
				"min_length": models.MIN_LENGTH_NEWS_TITLE,
				"error_messages": {
					"max_length": ERROR_FIELD(
						field = "titulo", 
						type = "largo",
						simbol = "menor o igual",
						value = models.MAX_LENGTH_NEWS_TITLE
					),
					"min_length": ERROR_FIELD(
						field = "titulo", 
						type = "corto",
						simbol = "mayor o igual",
						value = models.MIN_LENGTH_NEWS_TITLE
					)
				}

			},
			"status": {
				"error_messages": {
					"invalid_choice": STATUS_INVALID_CHOICE
				}
			}
		}

class NewsResponse(school_serializer.NewsDetailResponse):

	class Meta:
		model = models.News
		fields = "__all__"


class NewsListResponse(school_serializer.NewsListResponse):

	class Meta:
		model = models.News
		fields = ["id", "title", "created", "updated", "media", "status"]


class NewsUpdateRequest(serializers.ModelSerializer):
	class Meta:
		model = models.News
		fields = ["id", "title", "status", "description"]
		read_only_fields = ["id"]

		extra_kwargs = {
			"title": {
				"max_length": models.MAX_LENGTH_NEWS_TITLE,
				"min_length": models.MIN_LENGTH_NEWS_TITLE,
				"error_messages": {
					"max_length": ERROR_FIELD(
						field = "titulo", 
						type = "largo",
						simbol = "menor o igual",
						value = models.MAX_LENGTH_NEWS_TITLE
					),
					"min_length": ERROR_FIELD(
						field = "titulo", 
						type = "corto",
						simbol = "mayor o igual",
						value = models.MIN_LENGTH_NEWS_TITLE
					)
				}

			},
			"status": {
				"error_messages": {
					"invalid_choice": STATUS_INVALID_CHOICE
				}
			}
		}


class NewsUpdateImagesRequest(serializers.Serializer):
	media = serializers.ListField(
		child = serializers.ImageField(max_length = MAX_LENGTH_IMAGE_NAME)
	)



DAYWEEK_INVALID_CHOICE = f"El día de la semana elegido es invalido, debe ser entre: {models.DaysNumber.values}"

class TimeGroupRequest(serializers.ModelSerializer):
	daysweek = serializers.ListField(
		child = serializers.IntegerField(
			min_value = 1,
			max_value = 5,
			error_messages = {
				"min_value": DAYWEEK_INVALID_CHOICE,
				"max_value": DAYWEEK_INVALID_CHOICE,
			}
		),
		required = False
	)

	class Meta:
		model = models.TimeGroup
		fields = "__all__"
		read_only_fields = ["id"]
		extra_kwargs = {
			"type": {
				"max_length": models.MAX_LENGTH_TYPEGROUP_TYPE,
				"min_length": models.MIN_LENGTH_TYPEGROUP_TYPE,
				"error_messages": {
					"max_length":ERROR_FIELD(
						field = "tipo", 
						type = "largo",
						simbol = "menor o igual",
						value = models.MAX_LENGTH_TYPEGROUP_TYPE
					),
					"min_length": ERROR_FIELD(
						field = "tipo", 
						type = "corto",
						simbol = "mayor o igual",
						value = models.MIN_LENGTH_TYPEGROUP_TYPE
					)
				}
			}
		}

	def validate(self, data):
		opening_time = data.get("opening_time")
		closing_time = data.get("closing_time")

		if closing_time <= opening_time:
			raise serializers.ValidationError(
				models.OPENING_CLOSING_TIME, 
				code = "invalid_time"
			)

		return data


class OfficeHourRequest(serializers.ModelSerializer):
	time_group = TimeGroupRequest()
	description = serializers.CharField(
		max_length = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D,
		min_length = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D,
		error_messages = {
			"max_length":ERROR_FIELD(
				field = "descripción del intervalo", 
				type = "largo",
				simbol = "menor o igual",
				value = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D
			),
			"min_length": ERROR_FIELD(
				field = "descripción del intervalo", 
				type = "corto",
				simbol = "mayor o igual",
				value = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D
			)
		}
	)

	class Meta:
		model = models.OfficeHour
		fields = ["description", "time_group"]


OfficeHour = TypeVar("OfficeHour", bound = models.OfficeHour)

class OfficeHourUpdateRequest(serializers.Serializer):
	description = serializers.CharField(
		required = True,
		max_length = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D,
		min_length = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D,
		error_messages = {
			"max_length":ERROR_FIELD(
				field = "descripción del intervalo", 
				type = "largo",
				simbol = "menor o igual",
				value = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D
			),
			"min_length": ERROR_FIELD(
				field = "descripción del intervalo", 
				type = "corto",
				simbol = "mayor o igual",
				value = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D
			)
		}
	)

	def update(self, instance: OfficeHour, validated_data: dict[str, str]) -> OfficeHour:
		validated = school_dto.OfficeHourDTO(
			interval_description = validated_data.get(
				"description", 
				instance.interval_description
			)
		).data
		
		instance.interval_description = validated.get("interval_description")
		
		return instance


class TimeGroupResponse(serializers.ModelSerializer):
	daysweek = serializers.SlugRelatedField(
		many=True,
		read_only=True,
		slug_field='name'
    )
	
	class Meta:
		model = models.TimeGroup
		fields = "__all__"


class TimeGroupListResponse(TimeGroupResponse):
	class Meta:
		model = models.TimeGroup
		exclude = ["overview"]

class OfficeHourResponse(serializers.ModelSerializer):
	time_group = TimeGroupResponse(read_only = True)
	
	class Meta:
		model = models.OfficeHour
		fields = "__all__"


class OfficeHourListResponse(serializers.ModelSerializer):
	time_group = TimeGroupListResponse(read_only = True)

	class Meta:
		model = models.OfficeHour
		fields = ["id", "interval_description", "time_group"]