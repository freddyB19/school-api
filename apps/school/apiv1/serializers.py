from django.db.models import F

from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from apps.school import models

class SchoolResponse(serializers.ModelSerializer):
	class Meta:
		model = models.School
		fields = [
			"id",
			"name",
			"subdomain",
			"logo",
			"address",
			"mission",
			"private"
		]

class SchoolDetailResponse(serializers.ModelSerializer):
	class Meta:
		model = models.School
		fields = "__all__"


class SchoolShortResponse(serializers.ModelSerializer):
	class Meta:
		model = models.School
		fields = ["id", "name", "subdomain"]


class SchoolStaffSerializerResponse(serializers.ModelSerializer):
	class Meta:
		model = models.SchoolStaff
		fields = ["id", "name", "occupation"]


class GradeListResponse(serializers.ModelSerializer):
	class Meta:
		model = models.Grade
		fields = ["id", "name", "type", "section"]


class GradeDetailResponse(serializers.ModelSerializer):
	school = SchoolShortResponse(read_only = True)
	teacher = SchoolStaffSerializerResponse(many = True, read_only = True)
	
	class Meta:
		model = models.Grade
		fields = "__all__"


class InfraestructureMediaSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.InfraestructureMedia
		fields = "__all__"

@extend_schema_field(OpenApiTypes.URI)
class InfraestructureMediaField(serializers.RelatedField):
	def to_representation(self, value):
		image = value.first()
		return image.photo

class InfraestructureListResponse(serializers.ModelSerializer):
	media = InfraestructureMediaField(read_only = True)
	
	class Meta:
		model = models.Infraestructure
		fields = ["id", "name", "media"]




class InfraestructureDetailResponse(serializers.ModelSerializer):
	school = SchoolShortResponse(read_only = True)
	media = InfraestructureMediaSerializer(many = True, read_only = True)
	
	class Meta:
		model = models.Infraestructure
		fields = "__all__"


class ContactInfoResponse(serializers.ModelSerializer):
	class Meta:
		model = models.ContactInfo
		fields = ["id", "email", "phone"]


class DaysWeekResponse(serializers.ModelSerializer):
	class Meta:
		model = models.DaysWeek
		fields = ["name"]

class TimeGroupListResponse(serializers.ModelSerializer):
	daysweek = DaysWeekResponse(many = True, read_only = True)

	class Meta:
		model = models.TimeGroup
		fields = ["id", "type", "daysweek", "opening_time", "closing_time"]


class TimeGroupDetailResponse(serializers.ModelSerializer):
	daysweek = DaysWeekResponse(many = True, read_only = True)
	
	class Meta:
		model = models.TimeGroup
		exclude = ["active"]

class OfficeHourListResponse(serializers.ModelSerializer):
	time_group = TimeGroupListResponse(read_only = True)
	
	class Meta:
		model = models.OfficeHour
		fields = ["id", "interval_description", "time_group"]


class OfficeHourDetailResponse(serializers.ModelSerializer):
	school = SchoolShortResponse(read_only = True)
	time_group = TimeGroupDetailResponse(read_only = True)
	
	class Meta:
		model = models.OfficeHour
		fields = "__all__"


class SocialMediaResponse(serializers.ModelSerializer):
	class Meta:
		model = models.SocialMedia
		exclude = ["school", "id"]


class CulturalEventMediaSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.CulturalEventMedia
		fields = "__all__"

@extend_schema_field(OpenApiTypes.URI)
class CulturalEventMediaField(serializers.RelatedField):
	def to_representation(self, value):
		image = value.first()
		return image.photo


class CulturalEventListResponse(serializers.ModelSerializer):
	media = CulturalEventMediaField(read_only = True)
	
	class Meta:
		model = models.CulturalEvent
		fields = ["id", "title", "date", "media"]


class CulturalEventDetailResponse(serializers.ModelSerializer):
	school = SchoolShortResponse(read_only = True)
	media = CulturalEventMediaSerializer(many = True, read_only = True)

	class Meta:
		model = models.CulturalEvent
		fields = "__all__"


class CalendarListResponse(serializers.ModelSerializer):
	class Meta:
		model = models.Calendar
		fields = ["id", "title", "date"]


class CalendarDetailResponse(serializers.ModelSerializer):
	class Meta:
		model = models.Calendar
		exclude = ["school"]


class NotificationCDCEListResponse(serializers.ModelSerializer):
	
	class Meta:
		model = models.NotificationCDCE
		exclude = ["title", "created", "updated"]



class NotificationCDCEDetailResponse(serializers.ModelSerializer):
	school = SchoolShortResponse(read_only = True)

	class Meta:
		model = models.NotificationCDCE
		fields = "__all__"



class NewsMediaSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.NewsMedia
		fields = "__all__"

@extend_schema_field(OpenApiTypes.URI)
class NewsMediaField(serializers.RelatedField):
	def to_representation(self, value):
		image = value.first()
		return image.photo

class NewsListResponse(serializers.ModelSerializer):
	media = NewsMediaField(read_only = True)

	class Meta:
		model = models.News
		fields = ["id", "title", "created", "updated", "media"]


class NewsResponse(serializers.ModelSerializer):
	school = SchoolShortResponse(read_only = True)
	media = NewsMediaSerializer(many = True)

	class Meta:
		model = models.News
		fields = "__all__"

class NewsDetailResponse(serializers.ModelSerializer):
	school = SchoolShortResponse(read_only = True)
	media = NewsMediaSerializer(many = True)

	class Meta:
		model = models.News
		exclude = ["status"]



class PaymentInfoResponse(serializers.ModelSerializer):
	class Meta:
		model = models.PaymentInfo
		fields = ["id", "title", "photo", "description"]


class PaymentInfoDetailResponse(serializers.ModelSerializer):
	school = SchoolShortResponse(read_only = True)
	
	class Meta:
		model = models.PaymentInfo
		fields = "__all__"


class PaymentReportListResponse(serializers.ModelSerializer):
	grade = GradeListResponse(read_only = True)

	class Meta:
		model = models.PaymentReport
		fields = [
			"id", 
			"fullname_student", 
			"payment_detail", 
			"created", 
			"grade"
		]

class PaymentReportDetailResponse(serializers.ModelSerializer):
	grade = GradeListResponse(read_only = True)
	school = SchoolShortResponse(read_only = True)

	class Meta:
		model = models.PaymentReport
		fields = "__all__"


class CoordinateResponse(serializers.ModelSerializer):
	class Meta:
		model = models.Coordinate
		exclude = ["school", "id"]


class SettingFormatResponse(serializers.ModelSerializer):
	colors = serializers.SlugRelatedField(
		many=True,
		read_only=True,
		slug_field='color'
	)
	
	class Meta:
		model = models.SettingFormat
		exclude = ["school", "id"]



class DownloadListResponse(serializers.ModelSerializer):
	class Meta:
		model = models.Download
		exclude = ["school", "description"]


class DownloadDetailResponse(serializers.ModelSerializer):
	school = SchoolShortResponse(read_only = True)
	
	class Meta:
		model = models.Download
		fields = "__all__"



class RepositoryMediaFileSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.RepositoryMediaFile
		fields = "__all__"

@extend_schema_field(OpenApiTypes.URI)
class RepositoryMediaField(serializers.RelatedField):
	def to_representation(self, value):
		file = value.first()
		return file.file

class RepositoryListResponse(serializers.ModelSerializer):
	#media = RepositoryMediaField(read_only = True)
	
	class Meta:
		model = models.Repository
		fields = ["id", "name_project", "created", "updated"]


class RepositoryDetailResponse(serializers.ModelSerializer):
	school = SchoolShortResponse(read_only = True)
	media = RepositoryMediaFileSerializer(many = True, read_only = True)
	
	class Meta:
		model = models.Repository
		fields = "__all__"


class SchoolSettingColorsSerializer(serializers.Serializer):
	colors = serializers.ListField(child = serializers.CharField())


class ExtraActivitiePhotoSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.ExtraActivitiePhoto
		fields = "__all__"

class ExtraActivitieFileSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.ExtraActivitieFile
		fields = "__all__"


class ExtraActivitieScheduleSerializer(serializers.ModelSerializer):
	
	daysweek = serializers.SlugRelatedField(
		many=True,
		read_only=True,
		slug_field='name'
    )

	class Meta:
		model = models.ExtraActivitieSchedule
		exclude = ["active"]


class ExtraActivitieScheduleShortSerializer(serializers.ModelSerializer):
	daysweek = serializers.SlugRelatedField(
		many=True,
		read_only=True,
		slug_field='name'
    )

	class Meta:
		model = models.ExtraActivitieSchedule
		fields = ["daysweek", "opening_time", "closing_time"]

@extend_schema_field(OpenApiTypes.URI)
class ExtraActivitiePhotoField(serializers.RelatedField):
	def to_representation(self, value):
		image = value.first()
		return image.photo


class ExtraActivitieListResponse(serializers.ModelSerializer):
	photos = ExtraActivitiePhotoField(read_only = True)
	schedules = ExtraActivitieScheduleShortSerializer(many = True)

	class Meta:
		model = models.ExtraActivitie
		fields = ["id", "title", "photos", "schedules"]


class ExtraActivitieDetailResponse(serializers.ModelSerializer):
	photos = ExtraActivitiePhotoSerializer(many = True)
	files = ExtraActivitieFileSerializer(many = True)
	schedules = ExtraActivitieScheduleSerializer(many = True)
	school = SchoolShortResponse(read_only = True)

	class Meta:
		model = models.ExtraActivitie
		fields = [
			"id", 
			"title", 
			"photos",
			"files",
			"schedules",
			"description",
			"school",
		]

