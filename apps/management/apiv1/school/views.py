from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, response, status

from django_filters.rest_framework import DjangoFilterBackend

from apps.school import models as school_models

from apps.management.commands import commands
from apps.utils.result_commands import ResponseError

from . import serializers, permissions, filters, paginations


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
		serializer = self.get_serializer(
			data = request.data, 
			context = {"pk": pk}
		)

		if not serializer.is_valid():
			return response.Response(
				data = serializer.errors,
				status = status.HTTP_400_BAD_REQUEST
			)
		
		officehour = serializer.save()

		return response.Response(
			data = self.serializer_class(officehour).data,
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
