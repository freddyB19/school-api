from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import response, status, viewsets, mixins

from apps.school import models as school_models
from apps.school.apiv1 import serializers as school_serializers

from apps.management.commands import commands
from apps.utils.result_commands import ResponseError

from . import serializers, permissions

class DetailModelVS(viewsets.GenericViewSet, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):
	pass

class BaseSchoolVS(viewsets.GenericViewSet, mixins.UpdateModelMixin):
	permission_classes = [IsAuthenticated, permissions.IsUserPermission]


class SchoolUpdateVS(BaseSchoolVS):
	queryset = school_models.School.objects.all()
	serializer_class = school_serializers.SchoolDetailResponse
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.BelongToOurAdministrator
	]

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
			school,
			data=request.data,
			partial = True
		)

		if not serializer.is_valid():
			return response.Response(
				data = serializer.errors,
				status = status.HTTP_400_BAD_REQUEST,
			)

		school = serializer.save()

		return response.Response(
			data = self.serializer_class(school).data,
			status = status.HTTP_200_OK
		)


class NewsDetailUpdateDeleteVS(DetailModelVS):
	queryset = school_models.News.objects.all()
	serializer_class = serializers.MSchoolNewsResponse
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.NewsPermissionDetail
	]

	def get_serializer_class(self):
		UploadImages = "upload_images"
		IsUpdate = [
			"update",
			"partial_update"
		]

		if self.action in IsUpdate:
			return serializers.MSchoolNewsUpdateRequest
		elif self.action == UploadImages:
			return serializers.MSchoolNewsUpdateImagesRequest

		return self.serializer_class

	@action(detail = True, methods = ["patch"], url_name = "upload-images")
	def upload_images(self, request, pk = None):
		news = self.get_object()
		serializer = self.get_serializer(
			news,
			data=request.data,
			partial = True
		)

		if not serializer.is_valid():
			return response.Response(
				data = serializer.errors,
				status = status.HTTP_400_BAD_REQUEST,
			)

		news = serializer.save()

		return response.Response(
			data = self.serializer_class(news).data,
			status = status.HTTP_200_OK
		)

	@action(detail = True, methods = ["delete"], url_name = "delete-all-images")
	def delete_all_images(self, request, pk=None):
		news = self.get_object()

		news.media.all().delete()

		return response.Response(
			data = self.serializer_class(news).data,
			status = status.HTTP_200_OK
		)


class RepositoryDetailUpdateDeleteVS(DetailModelVS):
	queryset = school_models.Repository.objects.all()
	serializer_class = serializers.MSchoolRepositoryResponse
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.RepositoryPermissionDetail
	]

	def get_serializer_class(self):
		upload_images = "upload_images"
		is_update = [
			"update",
			"partial_update"
		]

		if self.action in is_update:
			return serializers.MSchoolRepositoryUpdateRequest
		elif self.action == upload_images:
			return serializers.MSchoolRepositoryUpdateMediaRequest

		return self.serializer_class

	def update(self, request, *args, **kwargs):
		partial = kwargs.get("partial", False)
		repository = self.get_object()
		serializer = self.get_serializer(
			repository, 
			data=request.data, 
			partial= partial,
			context = {"pk": repository.school_id}
		)

		serializer.is_valid(raise_exception=True)

		self.perform_update(serializer)

		return response.Response(
			data = serializer.data,
			status = status.HTTP_200_OK
		)

	@action(detail = True, methods = ["patch"], url_name = "upload-files")
	def upload_files(self, request, pk = None):
		repository = self.get_object()
		serializer = self.get_serializer(
			repository,
			data=request.data,
			partial = True
		)

		if not serializer.is_valid():
			return response.Response(
				data = serializer.errors,
				status = status.HTTP_400_BAD_REQUEST,
			)

		update_repository = serializer.save()

		return response.Response(
			data = self.serializer_class(update_repository).data,
			status = status.HTTP_200_OK
		)

	@action(detail = True, methods = ["delete"], url_name = "delete-all-files")
	def delete_all_files(self, request, pk=None):
		repository = self.get_object()

		repository.media.all().delete()

		return response.Response(
			data = self.serializer_class(repository).data,
			status = status.HTTP_200_OK
		)
