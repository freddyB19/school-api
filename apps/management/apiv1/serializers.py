from rest_framework import serializers

from apps.management import models
from apps.user.apiv1.serializers import UserResposeSerializer
from apps.school.apiv1.serializers import SchoolShortResponse


class AdministratorResponse(serializers.ModelSerializer):
	users = serializers.SerializerMethodField()
	detail = serializers.SerializerMethodField()
	total_users = serializers.SerializerMethodField()
 
	class Meta:
		model = models.Administrator
		fields = ["id", "users", "detail", "total_users"]

	def get_detail(self, obj) -> str:
		return obj.get_absolute_url()

	def get_users(self, obj) -> int:
		return UserResposeSerializer(obj.users.all()[:5], many = True).data

	def get_total_users(self, obj) -> int:
		return obj.users.count()


class AdministratorDetailResponse(serializers.ModelSerializer):
	users = UserResposeSerializer(many = True, read_only = True)
	school = SchoolShortResponse(read_only = True)
	total_users = serializers.SerializerMethodField()

	class Meta:
		model = models.Administrator
		fields = "__all__"

	def get_total_users(self, obj) -> int:
		return obj.users.count()
