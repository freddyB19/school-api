from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, response, status

from django_filters.rest_framework import DjangoFilterBackend

from apps.school import models

from . import serializers, permissions, filters, paginations


class NewsListCreateAPIView(generics.ListCreateAPIView):
	queryset = models.News.objects.all()
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


class NewsMediaDeleteAPIView(generics.RetrieveDestroyAPIView):
	queryset = models.NewsMedia.objects.all()
	serializer_class = serializers.MSchoolNewsMediaSerializer
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission
	]
	# ¿Es necesario tener un permiso que valide si una imagen forma parte
	# de una noticia que pertenece a una escuela de la que formamos parte 
	# como 'admins'?
	# Se puede, pero, debo hacer esto por cada tabla con esta similitud y
	# creo que es algo que no vale la pena, ya que serían múltiples permisos
	# personalizados, por lo que no lo vale.
	# Además, creo que las consultas para realizar esto tendrían que buscar 
	# en toda la tabla de noticias, ya que no se tiene un ID sobre 
	# qué noticia trata o a qué escuela pertenece la noticia que tiene estas
	# imagenes.



class OfficeHourListCreateAPIView(generics.ListCreateAPIView):
	queryset = models.OfficeHour.objects.all()
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
	queryset = models.OfficeHour.objects.all()
	serializer_class = serializers.MSchoolOfficeHourResponse
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.OfficeHourPermissionDetail
	]

	def get_serializer_class(self):
		update = ["PUT", "PATCH"]

		if self.request.method in update:
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


class TimeGroupListAPIView(generics.ListAPIView):
	queryset = models.TimeGroup.objects.all()
	serializer_class = serializers.MSchoolTimeGroupListResponse
	pagination_class = paginations.BasicPaginate
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.BelongToOurAdministrator
	]
	filter_backends = [DjangoFilterBackend]
	filterset_class = filters.TimeGroupFilter

	def get_queryset(self):
		return self.queryset.filter(
			intervalsList__school_id = self.kwargs.get("pk")
		).order_by("-id")


class TimeGroupDetailDeleteUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
	queryset = models.TimeGroup.objects.all()
	serializer_class = serializers.MSchoolTimeGroupResponse
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
	]

	def get_serializer_class(self):
		update = ["PATCH", "PUT"]
		if self.request.method in update:
			return serializers.MSchoolTimeGroupRequest
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
		
		time_group = serializer.save()

		return response.Response(
			data = self.serializer_class(time_group).data,
			status = status.HTTP_200_OK
		)


class CalendarListCreateAPIView(generics.ListCreateAPIView):
	queryset = models.Calendar.objects.all()
	serializer_class = serializers.MSchoolCalendarRequest
	pagination_class = paginations.CalendarPaginate
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.BelongToOurAdministrator
	]
	filter_backends = [DjangoFilterBackend]
	filterset_class = filters.CalendarFilter

	def get_queryset(self):
		current_year = timezone.localtime().year

		return self.queryset.filter(
			school_id = self.kwargs.get("pk"),
			date__year = current_year
		).order_by("date")

	def get_serializer_class(self):
		if self.request.method == "GET":
			return serializers.MSchoolCalendarListResponse
		
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

		calendar = serializer.save()

		return response.Response(
			data = self.serializer_class(calendar).data,
			status = status.HTTP_201_CREATED
		)

class CalendarDetailDeleteUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
	queryset = models.Calendar.objects.all()
	serializer_class = serializers.MSchoolCalendarResponse
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.CalendarPermissionDetail
	]

	def get_serializer_class(self):
		update = ["PATCH", "PUT"]
		if self.request.method in update:
			return serializers.MSchoolCalendarUpdateRequest
		return self.serializer_class


class SocialMediaListCreateAPIView(generics.ListCreateAPIView):
	queryset = models.SocialMedia.objects.all()
	serializer_class = serializers.MSchoolSocialMediaReponse
	pagination_class = paginations.BasicPaginate
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.BelongToOurAdministrator
	]

	def get_queryset(self):
		return self.queryset.filter(
			school_id = self.kwargs.get("pk"),
		).order_by("id")

	def get_serializer_class(self):
		
		if self.request.method == "POST":
			return serializers.MSchoolSocialMediaResquest
		
		return self.serializer_class

	def is_bulk_create(self, initial_data: dict) -> bool:
		return True if initial_data.get("profiles") else False

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

		social_media = serializer.save()

		many = self.is_bulk_create(initial_data = serializer.initial_data)
		
		return response.Response(
			data = self.serializer_class(social_media, many = many).data,
			status = status.HTTP_201_CREATED
		)


class SocialMediaDetailDeleteUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
	queryset = models.SocialMedia.objects.all()
	serializer_class = serializers.MSchoolSocialMediaReponse
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.SocialMediaPermissionDetail
	]

	def get_serializer_class(self):
		update = ["PATCH", "PUT"]
		if self.request.method in update:
			return serializers.MSchoolSocialMediaUpdateRequest
		return self.serializer_class


class CoordinateListCreateAPIView(generics.ListCreateAPIView):
	queryset = models.Coordinate.objects.all()
	serializer_class = serializers.MSchoolCoordinateRequest 
	pagination_class = paginations.BasicPaginate
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.BelongToOurAdministrator
	]

	def get_queryset(self):
		return self.queryset.filter(
			school_id = self.kwargs.get("pk"),
		).order_by("id")

	def get_serializer_class(self):
		if self.request.method == "GET":
			return serializers.MSchoolCoordinateResponse 
		
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

		coordinate = serializer.save()

		return response.Response(
			data = self.serializer_class(coordinate).data,
			status = status.HTTP_201_CREATED
		)


class CoordinateDetailDeleteUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
	queryset = models.Coordinate.objects.all()
	serializer_class = serializers.MSchoolCoordinateResponse
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.CoordinatePermissionDetail
	]

	def get_serializer_class(self):
		update = ["PATCH", "PUT"]

		if self.request.method in update:
			return serializers.MSchoolCoordinateUpdateRequest
		return self.serializer_class


class StaffListCreateAPIView(generics.ListCreateAPIView):
	queryset = models.SchoolStaff.objects.all()
	serializer_class = serializers.MSchoolStaffRequest
	pagination_class = paginations.BasicPaginate
	permission_classes = [
		IsAuthenticated, 
		permissions.IsUserPermission,
		permissions.BelongToOurAdministrator
	]
	filter_backends = [DjangoFilterBackend]
	filterset_class = filters.StaffFilter


	def get_queryset(self):
		return self.queryset.filter(
			school_id = self.kwargs.get("pk"),
		).order_by("id")

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

		staff = serializer.save()

		return response.Response(
			data = self.serializer_class(staff).data,
			status = status.HTTP_201_CREATED
		)