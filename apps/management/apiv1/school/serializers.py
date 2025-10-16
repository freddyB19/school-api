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

ERROR_FIELD = lambda field, type, symbol, value: f"El campo '{field}' es muy {type}, debe ser {symbol} a {value}" 

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
						symbol = "menor o igual",
						value = models.MAX_LENGTH_SCHOOL_NAME
					),
					"min_length": ERROR_FIELD(
						field = "nombre", 
						type = "corto",
						symbol = "mayor o igual",
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
						symbol = "menor o igual",
						value = models.MAX_LENGTH_SCHOOL_ADDRESS
					),
					"min_length": ERROR_FIELD(
						field = "misión",
						type = "corto",
						symbol = "mayor o igual",
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
						symbol = "mayor o igual",
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
						symbol = "mayor o igual",
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
						symbol = "mayor o igual",
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
						symbol = "menor o igual",
						value = models.MAX_LENGTH_NEWS_TITLE
					),
					"min_length": ERROR_FIELD(
						field = "titulo", 
						type = "corto",
						symbol = "mayor o igual",
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
						symbol = "menor o igual",
						value = models.MAX_LENGTH_NEWS_TITLE
					),
					"min_length": ERROR_FIELD(
						field = "titulo", 
						type = "corto",
						symbol = "mayor o igual",
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

class MSchoolTimeGroupRequest(serializers.ModelSerializer):
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
						symbol = "menor o igual",
						value = models.MAX_LENGTH_TYPEGROUP_TYPE
					),
					"min_length": ERROR_FIELD(
						field = "tipo", 
						type = "corto",
						symbol = "mayor o igual",
						value = models.MIN_LENGTH_TYPEGROUP_TYPE
					)
				}
			}
		}

	def validate(self, data):

		opening_time = data.get("opening_time")
		closing_time = data.get("closing_time")

		if not opening_time and not closing_time:
			return data

		time = [opening_time, closing_time]
		INVALID_TIME_SENT = None 
		TOTAL_INVALID_DATA_SENT_TIME = 1
		ERROR_MESSAGE = "Debe enviar ámbos valores [opening_time, closing_time]"

		if time.count(INVALID_TIME_SENT) == TOTAL_INVALID_DATA_SENT_TIME:
			# Validamos si solo se ha enviado un solo valor
			# en relación con [opening_time, closing_time]
			
			raise serializers.ValidationError(
				ERROR_MESSAGE,
				code="invalid_request"
			)

		if closing_time <= opening_time:
			raise serializers.ValidationError(
				models.OPENING_CLOSING_TIME, 
				code = "invalid_time"
			)

		return data

SCHOOL_DOES_NOT_EXIST = "No existe una 'escuela' con ese id"
TIMEGROUP_DOES_NOT_EXIST = "No existe un 'grupo horario' con ese id"
INVALID_TIMEGROUP = "Debe definir un nuevo 'grupo horario' o seleccionar uno ya existente"

class MSchoolOfficeHourRequest(serializers.ModelSerializer):
	time_group = MSchoolTimeGroupRequest(required = False)
	time_group_id = serializers.IntegerField(
		required = False,
		min_value = 1
	)
	description = serializers.CharField(
		max_length = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D,
		min_length = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D,
		error_messages = {
			"max_length":ERROR_FIELD(
				field = "descripción del intervalo", 
				type = "largo",
				symbol = "menor o igual",
				value = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D
			),
			"min_length": ERROR_FIELD(
				field = "descripción del intervalo", 
				type = "corto",
				symbol = "mayor o igual",
				value = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D
			)
		}
	)

	class Meta:
		model = models.OfficeHour
		fields = ["description", "time_group", 'time_group_id']

	def validate_time_group_id(self, value):
		school = commands.get_school_by_id(
			id = self.context.get("pk")
		).query

		if not school:
			raise serializers.ValidationError(
				SCHOOL_DOES_NOT_EXIST,
				code="does-not-exist"
			)
			
		if not school.officeHoursList.filter(time_group_id = value).exists():
			raise serializers.ValidationError(
				TIMEGROUP_DOES_NOT_EXIST,
				code="does-not-exist"
			)

		return value


	def validate(self, data):
		time_group = data.get("time_group")
		time_group_id = data.get("time_group_id")

		if not time_group and not time_group_id:
			raise serializers.ValidationError(
				INVALID_TIMEGROUP,
				code="required"
			)

		if time_group and time_group_id:
			raise serializers.ValidationError(
				INVALID_TIMEGROUP,
				code="invalid"
			)

		return data


	def create(self, validated_data):

		new_time_group = validated_data.get("time_group")
		time_group_id = validated_data.get("time_group_id")

		time_group = new_time_group or school_dto.TimeGroupByIdDTO(id = time_group_id)

		office_hour = school_dto.OffiHourCreateDTO(
			description = validated_data.get("description"),
			time_group = time_group
		).data

		command = commands.create_office_hour(
			school_id = self.context.get("pk"),
			office_hour = office_hour,
		)

		if not command.status:
			raise serializers.ValidationError(
				ResponseError(
					errors = command.errors
				).model_dump(exclude_defaults = True)
			)

		return command.query



OfficeHour = TypeVar("OfficeHour", bound = models.OfficeHour)

class MSchoolOfficeHourUpdateRequest(serializers.Serializer):
	description = serializers.CharField(
		required = True,
		max_length = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D,
		min_length = models.MIN_LENGTH_OFFICEHOUR_INTERVAL_D,
		error_messages = {
			"max_length":ERROR_FIELD(
				field = "descripción del intervalo", 
				type = "largo",
				symbol = "menor o igual",
				value = models.MAX_LENGTH_OFFICEHOUR_INTERVAL_D
			),
			"min_length": ERROR_FIELD(
				field = "descripción del intervalo", 
				type = "corto",
				symbol = "mayor o igual",
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


class MSchoolTimeGroupResponse(serializers.ModelSerializer):
	daysweek = serializers.SlugRelatedField(
		many=True,
		read_only=True,
		slug_field='name'
    )
	
	class Meta:
		model = models.TimeGroup
		fields = "__all__"


class MSchoolTimeGroupListResponse(MSchoolTimeGroupResponse):
	class Meta:
		model = models.TimeGroup
		exclude = ["overview"]

class MSchoolOfficeHourResponse(serializers.ModelSerializer):
	time_group = MSchoolTimeGroupResponse(read_only = True)
	
	class Meta:
		model = models.OfficeHour
		fields = "__all__"


class MSchoolOfficeHourListResponse(serializers.ModelSerializer):
	time_group = MSchoolTimeGroupListResponse(read_only = True)

	class Meta:
		model = models.OfficeHour
		fields = ["id", "interval_description", "time_group"]


class MSchoolCalendarListResponse(serializers.ModelSerializer):
	class Meta:
		model = models.Calendar
		fields = ["id", "title", "date"]


class MSchoolCalendarRequest(serializers.ModelSerializer):
	class Meta:
		model = models.Calendar
		fields = ["title", "description", "date"]
		extra_kwargs = {
			"title": {
				"min_length": models.MIN_LENGTH_CALENDAR_TITLE,
				"max_length": models.MAX_LENGTH_CALENDAR_TITLE,
				"error_messages": {
					"min_length": ERROR_FIELD(
						field = "titulo", 
						type = "corto",
						symbol = "mayor o igual",
						value = models.MIN_LENGTH_CALENDAR_TITLE
					),
					"max_length": ERROR_FIELD(
						field = "titulo", 
						type = "largo",
						symbol = "menor o igual",
						value = models.MAX_LENGTH_CALENDAR_TITLE
					),
				}
			}
		}

	def validate(self, data):
		title = data.get("title")
		date = data.get("date")
 
		calendar = commands.calendar_exist(
			school_id = self.context.get("pk"), 
			title = title, 
			date = date
		).query
		
		if calendar:
			raise serializers.ValidationError(
				"Ya existe un registro con el mismo título y fecha",
				code="already_exists"
			)
			
		return data


	def create(self, validated_data):

		command  = commands.create_calendar(
			school_id = self.context.get("pk"),
			calendar = validated_data
		)

		if not command.status:
			raise serializers.ValidationError(
				ResponseError(
					errors = command.errors
				).model_dump(exclude_defaults = True),
				code = "invalid"
			)

		return command.query


class MSchoolCalendarResponse(serializers.ModelSerializer):
	class Meta:
		model = models.Calendar
		exclude = ["school"]
