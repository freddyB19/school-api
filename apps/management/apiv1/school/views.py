from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, response, status, viewsets, mixins

from django_filters.rest_framework import DjangoFilterBackend

from apps.school import models as school_models
from apps.school.apiv1 import serializers as school_serializer

from apps.management.commands import commands
from apps.utils.result_commands import ResponseError

from . import serializers, permissions, filters, paginations


class BaseVS(viewsets.GenericViewSet, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.BelongToOurAdministrator
	]

class BaseSchoolVS(viewsets.GenericViewSet, mixins.UpdateModelMixin):
	permission_classes = [IsAuthenticated, permissions.IsUserPermission]


class SchoolUpdateVS(BaseSchoolVS):
	queryset = school_models.School.objects.all()
	serializer_class = school_serializer.SchoolDetailResponse
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


class NewsListCreateAPIView(generics.ListCreateAPIView):
	queryset = school_models.News.objects.all()
	serializer_class = serializers.NewsResponse
	pagination_class = paginations.BasicPaginate
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.BelongToOurAdministrator
	]
	filter_backends = [DjangoFilterBackend]
	filterset_class = filters.NewsFilter

	def get_queryset(self):
		return self.queryset.filter(
			school_id = self.kwargs.get("pk")
		)

	def get_serializer_class(self):

		if self.request.method == "POST":
			return serializers.NewsRequest
		elif self.request.method == "GET":
			return serializers.NewsListResponse

		return self.serializer_class


	def post(self, request, pk = None):

		serializer = self.get_serializer(data = request.data)

		if not serializer.is_valid():
			return response.Response(
				data = serializer.errors,
				status = status.HTTP_400_BAD_REQUEST
			)

		command = commands.create_news(
			school_id = pk,
			news = serializer.data,
			images = request.FILES
		)

		if not command.status:
			return response.Response(
				data = ResponseError(
					errors = command.errors
				).model_dump(),
				status = command.error_code
			)

		news = command.query

		return response.Response(
			data = self.serializer_class(news).data,
			status = status.HTTP_201_CREATED
		)


class NewsDetailUpdateDeleteVS(BaseVS):
	queryset = school_models.News.objects.all()
	serializer_class = serializers.NewsResponse

	def get_serializer_class(self):

		if self.action == "update" or self.action == "partial_update":
			return serializers.NewsUpdateRequest
		elif self.action == "upload_images":
			return serializers.NewsUpdateImagesRequest

		return self.serializer_class

	@action(detail = True, methods = ["patch"], url_name = "upload-images")
	def upload_images(self, request, pk = None):
		news = self.get_object()
		serializer = self.get_serializer(
			data=request.data,
		)

		if not serializer.is_valid():
			return response.Response(
				data = serializer.errors,
				status = status.HTTP_400_BAD_REQUEST,
			)

		command = commands.update_news_media(images = request.FILES)

		if not command.status:
			return response.Response(
				data = ResponseError(
					errors = command.errors
				).model_dump(),
				status = status.HTTP_400_BAD_REQUEST
			)
		
		news.media.add(*command.query)
		news.save()

		return response.Response(
			data = self.serializer_class(news).data,
			status = status.HTTP_200_OK
		)


class OfficeHourListCreateAPIView(generics.ListCreateAPIView):
	queryset = school_models.OfficeHour.objects.all()
	serializer_class = serializers.OfficeHourResponse 
	pagination_class = paginations.BasicPaginate
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.BelongToOurAdministrator
	]
	filter_backends = [DjangoFilterBackend]
	filterset_class = filters.OfficeHourFilter
	

	def get_queryset(self):
		return self.queryset.filter(
			school_id = self.kwargs.get("pk")
		).order_by("-id")

	def get_serializer_class(self):
		
		if self.request.method == "POST":
			return serializers.OfficeHourRequest
		elif self.request.method == "GET":
			return serializers.OfficeHourListResponse	
		
		return self.serializer_class


	def post(self, request, pk = None):
		serializer = self.get_serializer(data = request.data)

		if not serializer.is_valid():
			return response.Response(
				data = serializer.errors,
				status = status.HTTP_400_BAD_REQUEST
			)
		
		command = commands.create_office_hour(
			school_id = pk,
			office_hour = serializer.data,
		)

		if not command.status:
			return response.Response(
				data = ResponseError(
					errors = command.errors
				).model_dump(exclude_defaults = True),
				status = command.error_code
			)

		news = command.query

		return response.Response(
			data = self.serializer_class(news).data,
			status = status.HTTP_201_CREATED
		)


class OfficeHourDetaiUpdateDeletelAPIView(generics.RetrieveUpdateDestroyAPIView):
	queryset = school_models.OfficeHour.objects.all()
	serializer_class = serializers.OfficeHourResponse
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.BelongToOurAdministrator
	]

	def get_serializer_class(self):
		updated = ["PUT", "PATCH"]

		if self.request.method in updated:
			return serializers.OfficeHourUpdateRequest

		return self.serializer_class

	def update(self, request, pk, *args, **kwargs):
		partial = kwargs.pop('partial', False)
		
		instance = self.get_object()
		
		serializer = self.get_serializer(
			instance, 
			data=request.data, 
			partial=partial
		)
		
		serializer.is_valid(raise_exception=True)
		
		officehour = serializer.save()

		return response.Response(
			data = self.serializer_class(officehour).data,
			status = status.HTTP_200_OK
		)
