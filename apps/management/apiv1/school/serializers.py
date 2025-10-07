from typing import TypeVar
from datetime import datetime

from rest_framework import serializers

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field


from apps.school import models

from apps.utils.result_commands import ResponseError

from apps.school.apiv1 import serializers as school_serializer

from apps.management.commands import commands
from apps.management.dtos import school as school_dto

ERROR_FIELD = lambda field, type, simbol, value: f"El campo '{field}' es muy {type}, debe ser {simbol} a {value}" 

MIN_LENGTH_FIELDS = 10

class SchoolUpdateRequest(serializers.ModelSerializer):
	class Meta:
		model = models.School
		exclude = ["private", "logo"]

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

class MSchoolNewsRequest(serializers.ModelSerializer):
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

	def create(self, validated_data) -> models.News:

		school_id = self.context.get("pk")
		
		validated = school_dto.NewsCreateDTO(
			images = validated_data.get("media"),
			**validated_data
		)

		command = commands.create_news(
			school_id = school_id,
			news = validated.data,
			images = validated.images
		)

		if not command.status:
			raise serializers.ValidationError(
				ResponseError(
					errors = command.errors,
				).model_dump(exclude_defaults = True)
			)

		return command.query


class MSchoolNewsMediaSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.NewsMedia
		fields = "__all__"

@extend_schema_field(OpenApiTypes.URI)
class MSchoolNewsMediaField(serializers.RelatedField):
	def to_representation(self, value):
		image = value.first()
		return image.photo if image else None


class MSchoolNewsResponse(serializers.ModelSerializer):
	media = MSchoolNewsMediaSerializer(many = True)
	
	class Meta:
		model = models.News
		fields = "__all__"


class MSchoolNewsListResponse(serializers.ModelSerializer):
	media = MSchoolNewsMediaField(read_only = True)

	class Meta:
		model = models.News
		fields = ["id", "title", "created", "updated", "media", "status"]


class MSchoolNewsUpdateRequest(serializers.ModelSerializer):
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


class MSchoolNewsUpdateImagesRequest(serializers.Serializer):
	media = serializers.ListField(
		child = serializers.ImageField(max_length = MAX_LENGTH_IMAGE_NAME)
	)

	def update(self, instance, validated_data) -> models.News:
		validated = school_dto.NewsUpdateImages(
			images = validated_data.get("media")
		)

		command = commands.update_news_media(images = validated.images)

		if not command.status:
			raise serializers.ValidationError(
				ResponseError(
					errors = command.errors
				).model_dump(exclude_defaults = True)
			)
		
		instance.media.add(*command.query)		

		return instance


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


	def create(self, validated_data):

		command = commands.create_office_hour(
			school_id = self.context.get("pk"),
			office_hour = validated_data,
		)

		if not command.status:
			raise serializers.ValidationError(
				ResponseError(
					errors = command.errors
				).model_dump(exclude_defaults = True)
			)

		return command.query



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
		validated = school_dto.OfficeHourUpdateDTO(
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