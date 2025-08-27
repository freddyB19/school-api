from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, response, status, viewsets, mixins

from apps.school import models
from apps.school.apiv1 import serializers as school_serializer
from apps.utils.result_commands import ResponseError
from apps.management.commands import commands

from . import serializers, permissions


class BaseSchoolVS(viewsets.GenericViewSet, mixins.UpdateModelMixin):
	permission_classes = [IsAuthenticated, permissions.IsUserPermission]


class SchoolUpdateVS(BaseSchoolVS):
	queryset = models.School.objects.all()
	serializer_class = school_serializer.SchoolDetailResponse

	def get_serializer_class(self):
		if self.action == "update" or self.action == "partial_update":
			return serializers.SchoolUpdateRequest
		elif self.action == "upload_image":
			return serializers.SchoolUpdateLogoRequest

		return self.serializer_class


	def update(self, request, *args, **kwargs):
		partial = kwargs.get("partial", False)
		
		school = self.get_object()

		serializer = self.get_serializer(
			school, 
			data=request.data, 
			partial=partial
		)

		if not serializer.is_valid():
			return response.Response(
				data = serializer.errors,
				status = status.HTTP_400_BAD_REQUEST,
			)

		self.perform_update(serializer)

		return response.Response(
			data = serializer.data,
			status = status.HTTP_200_OK
		)

	@action(detail = True, methods = ["patch"], url_name = "upload-image")
	def upload_image(self, request, pk = None):
		school = self.get_object()
		serializer = self.get_serializer(
			data=request.data,
		)

		if not serializer.is_valid():
			return response.Response(
				data = serializer.errors,
				status = status.HTTP_400_BAD_REQUEST,
			)

		command = commands.update_school_logo(image = request.data["logo"])

		if not command.status:
			return response.Response(
				data = ResponseError(
					errors = command.errors
				).model_dump()
			)
		
		school.logo = command.query
		school.save()

		return response.Response(
			data = self.serializer_class(school).data,
			status = status.HTTP_200_OK
		)
