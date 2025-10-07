from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, response, status

from django_filters.rest_framework import DjangoFilterBackend

from apps.school import models as school_models

from . import serializers, permissions, filters, paginations


class NewsListCreateAPIView(generics.ListCreateAPIView):
	queryset = school_models.News.objects.all()
	serializer_class = serializers.MSchoolNewsResponse
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
			return serializers.MSchoolNewsRequest
		elif self.request.method == "GET":
			return serializers.MSchoolNewsListResponse

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

		news = serializer.save()

		return response.Response(
			data = self.serializer_class(news).data,
			status = status.HTTP_201_CREATED
		)


class OfficeHourListCreateAPIView(generics.ListCreateAPIView):
	queryset = school_models.OfficeHour.objects.all()
	serializer_class = serializers.MSchoolOfficeHourResponse 
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
			return serializers.MSchoolOfficeHourRequest
		elif self.request.method == "GET":
			return serializers.MSchoolOfficeHourListResponse	
		
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
	serializer_class = serializers.MSchoolOfficeHourResponse
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.BelongToOurAdministrator
	]

	def get_serializer_class(self):
		updated = ["PUT", "PATCH"]

		if self.request.method in updated:
			return serializers.MSchoolOfficeHourUpdateRequest

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
