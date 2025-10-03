from django.utils import timezone

from django.db.models import F

from rest_framework import (
	permissions,
	views,
	generics,
	status,
	response
)

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes

from apps.utils.result_commands import (
    MessageError,
    ResponseSuccess,
    ResponseError
)

from . import paginations
from . import serializers
from apps.school import models



class SchoolAPIView(views.APIView):
	@extend_schema(
		methods=["GET"],
		auth=None,
		operation_id = "school_retrieve_by_query",
		responses = {
			422: ResponseError, 
			404: ResponseError, 
			200: serializers.SchoolResponse
		},
		parameters=[
			OpenApiParameter(
                name="subdomain",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Search school by subdomain"
            )
		]
	)

	def get(self, request):

		query_subdomain = request.query_params.get("subdomain")

		if not query_subdomain:
			return response.Response(
				ResponseError(
					errors = [
						{"message": "Debe enviar un valor en el parametro de busqueda"}
					]
				).model_dump(), 
				status = status.HTTP_422_UNPROCESSABLE_ENTITY
			)

		try:
			school = models.School.objects.values(
				"id",
				"name",
				"subdomain",
				"logo",
				"address",
				"mission",
				"private"
			).get(subdomain = query_subdomain)
		except models.School.DoesNotExist as e:

			return response.Response(
				ResponseError(
					errors = [
						{"message": "No existe información sobre esta escuela"}
					]
				).model_dump(), 
				status = status.HTTP_404_NOT_FOUND
			)

		de_serializer = serializers.SchoolResponse(school)
		
		return response.Response(
			data = de_serializer.data,
			status = status.HTTP_200_OK
		)


class SchoolDetailAPIView(generics.RetrieveAPIView):
	queryset = models.School.objects.all()
	serializer_class = serializers.SchoolDetailResponse


class SettingsFormatAPIView(generics.RetrieveAPIView):
	queryset = models.SettingFormat.objects.all()
	serializer_class = serializers.SettingFormatResponse

	def get_object(self):
		return self.queryset.get(
			school_id = self.kwargs.get("pk")
		)

class OfficeHourList(generics.ListAPIView):
	queryset = models.OfficeHour.objects.all()
	serializer_class = serializers.OfficeHourListResponse
	pagination_class = paginations.BasicPaginate

	def get_queryset(self):
		return self.queryset.select_related(
			"time_group"
		).filter(
			school_id = self.kwargs.get("pk")
		).order_by("-id")


class OfficeHourDetailAPIView(generics.RetrieveAPIView):
	queryset = models.OfficeHour.objects.all()
	serializer_class = serializers.OfficeHourDetailResponse

	def get_object(self):
		try:
			return self.queryset.select_related(
				"school", "time_group"
			).get(pk = self.kwargs.get("pk"))
		except models.OfficeHour.DoesNotExist as e:
			return None

	def retrieve(self, request, *args, **kwargs):
		obj = self.get_object()

		if not obj:
			return response.Response(
				data = {
					"error": {"message": f"No existe información sobre algún horario de oficina con este id ({kwargs.get('pk')})"}
				},
				status = status.HTTP_404_NOT_FOUND
			)

		serializer = self.get_serializer(obj)

		return response.Response(data = serializer.data, status = status.HTTP_200_OK)

		


class CalendarListAPIView(generics.ListAPIView):
	queryset = models.Calendar.objects.all()
	serializer_class = serializers.CalendarListResponse
	pagination_class = paginations.BasicPaginate

	def get_queryset(self):
		query_param = self.request.query_params.get("month")
		
		if not query_param:
			query_param = datetime.now().month
 
		return self.queryset.filter(
			school_id = self.kwargs.get("pk"),
			date__month = query_param
		).order_by("date")


class CalendarDetailAPIView(generics.RetrieveAPIView):
	queryset = models.Calendar.objects.all()
	serializer_class = serializers.CalendarDetailResponse


class SocialMediaListAPIView(generics.ListAPIView):
	queryset = models.SocialMedia.objects.all()
	serializer_class = serializers.SocialMediaResponse
	pagination_class = paginations.BasicPaginate
	#Necesita una paginación diferente

	def get_queryset(self):
		return self.queryset.filter(
			school_id = self.kwargs.get("pk")
		).order_by("id")


class CoordinateListAPIView(generics.ListAPIView):
	queryset = models.Coordinate.objects.all()
	serializer_class = serializers.CoordinateResponse

	def get_queryset(self):
		return self.queryset.filter(
			school_id = self.kwargs.get("pk")
		).order_by("id")


class GradesListAPiView(generics.ListAPIView):
	queryset = models.Grade.objects.all()
	serializer_class = serializers.GradeListResponse
	pagination_class = paginations.BasicPaginate
	
	def get_queryset(self):
		return self.queryset.filter(
			school_id = self.kwargs.get("pk")
		)


class GradeDetailAPIView(generics.RetrieveAPIView):
	queryset = models.Grade.objects.all()
	serializer_class = serializers.GradeDetailResponse

	def get_object(self):
		try:
			return self.queryset.prefetch_related(
				"teacher"
			).select_related(
				"school"
			).get(
				pk = self.kwargs.get("pk")
			)
		except models.Grade.DoesNotExist as e:
			return None

	def retrieve(self, request, *args, **kwargs):
		obj = self.get_object()

		if not obj:
			return response.Response(
				data = {
					"error": {"message": f"No existe información sobre algún nivel escolar con este id ({kwargs.get('pk')})"}
				},
				status = status.HTTP_404_NOT_FOUND
			)

		serializer = self.get_serializer(obj)

		return response.Response(data = serializer.data, status = status.HTTP_200_OK)


class RepositoryListAPIView(generics.ListAPIView):
	queryset = models.Repository.objects.all()
	serializer_class = serializers.RepositoryListResponse
	pagination_class = paginations.BasicPaginate

	def get_queryset(self):
		return self.queryset.filter(
			school_id = self.kwargs.get("pk")
		).order_by("-created", "-updated")


class RepositoryDetailAPIView(generics.RetrieveAPIView):
	queryset = models.Repository.objects.all()
	serializer_class = serializers.RepositoryDetailResponse

	def get_object(self):
		try:
			return self.queryset.prefetch_related(
				"media"
			).select_related(
				"school"
			).get(pk = self.kwargs.get("pk"))

		except models.Repository.DoesNotExist as e:
			return None
		
	def retrieve(self, request, *args, **kwargs):
		obj = self.get_object()

		if not obj:
			return response.Response(
				data = {
					"error": {"message": f"No existe información sobre algún respositorio con este id ({kwargs.get('pk')})"}
				},
				status = status.HTTP_404_NOT_FOUND
			)

		serializer = self.get_serializer(obj)

		return response.Response(data = serializer.data, status = status.HTTP_200_OK)


class InfraestructureListAPIView(generics.ListAPIView):
	queryset = models.Infraestructure.objects.all()
	serializer_class = serializers.InfraestructureListResponse
	pagination_class = paginations.BasicPaginate

	def get_queryset(self):
		return self.queryset.filter(
			school_id = self.kwargs.get("pk")
		).order_by("id")


class InfraestructureDetailAPIView(generics.RetrieveAPIView):
	queryset = models.Infraestructure.objects.all()
	serializer_class = serializers.InfraestructureDetailResponse
	
	def get_object(self):
		try:
			return self.queryset.prefetch_related(
				"media",
			).select_related(
				"school"
			).get(
				pk = self.kwargs.get("pk")
			)
		except models.Infraestructure.DoesNotExist as e:
			return None

	def retrieve(self, request, *args, **kwargs):
		obj = self.get_object()

		if not obj:
			return response.Response(
				data = {
					"error": {"message": f"No existe una infraestructura con este id ({kwargs.get('pk')})"}
				},
				status = status.HTTP_404_NOT_FOUND
			)

		serializer = self.get_serializer(obj)

		return response.Response(data = serializer.data, status = status.HTTP_200_OK)
		  

class DownloadsListAPIView(generics.ListAPIView):
	queryset = models.Download.objects.all()
	serializer_class = serializers.DownloadListResponse
	pagination_class = paginations.BasicPaginate

	def get_queryset(self):
		return self.queryset.filter(
			school_id = self.kwargs.get("pk")
		).order_by("id")


class DownloadsDetailAPIView(generics.RetrieveAPIView):
	queryset = models.Download.objects.all()
	serializer_class = serializers.DownloadDetailResponse

	def get_object(self):
		try:
			return self.queryset.select_related(
				"school"
			).get(
				pk = self.kwargs.get("pk")
			)
		except models.Download.DoesNotExist as e:
			return None

	def retrieve(self, request, *args, **kwargs):
		obj = self.get_object()

		if not obj:
			return response.Response(
				data = {
					"error": {"message": f"No existe un archivo con este id ({kwargs.get('pk')})"}
				},
				status = status.HTTP_404_NOT_FOUND
			)

		serializer = self.get_serializer(obj)

		return response.Response(data = serializer.data, status = status.HTTP_200_OK)

		

class NewsListAPIView(generics.ListAPIView):
	queryset = models.News.objects.all()
	serializer_class = serializers.NewsListResponse
	pagination_class = paginations.BasicPaginate

	def get_queryset(self):
		return self.queryset.filter(
			school_id = self.kwargs.get("pk")
		).order_by("-created", "-updated")


class NewsDetailAPIView(generics.RetrieveAPIView):
	queryset = models.News.objects.all()
	serializer_class = serializers.NewsDetailResponse

	def get_object(self):
		try:
			return self.queryset.prefetch_related(
			"media"
			).select_related(
				"school"
			).get(
				pk = self.kwargs.get("pk")
			)
		except models.News.DoesNotExist as e:
			return None

	def retrieve(self, request, *args, **kwargs):
		obj = self.get_object()

		if not obj:
			return response.Response(
				data = {
					"error": {"message": f"No existe una noticia con este id ({kwargs.get('pk')})"}
				},
				status = status.HTTP_404_NOT_FOUND
			)

		serializer = self.get_serializer(obj)

		return response.Response(data = serializer.data, status = status.HTTP_200_OK)
		

class CulturalEventsListAPIView(generics.ListAPIView):
	queryset = models.CulturalEvent.objects.all()
	serializer_class = serializers.CulturalEventListResponse
	pagination_class = paginations.BasicPaginate


	def get_queryset(self):
		return self.queryset.filter(
			school_id = self.kwargs.get("pk")
		)

class CulturalEventsDetailAPIView(generics.RetrieveAPIView):
	queryset = models.CulturalEvent.objects.all()
	serializer_class = serializers.CulturalEventDetailResponse


	def get_object(self):
		try:
			return self.queryset.prefetch_related(
				"media"
			).select_related(
				"school"
			).get(
				pk = self.kwargs.get("pk")
			)
		except models.CulturalEvent.DoesNotExist as e:
			return None
	
	def retrieve(self, request, *args, **kwargs):
		obj = self.get_object()

		if not obj:
			return response.Response(
				data = {
					"error": {"message": f"No existe algún evento cultural con este id ({kwargs.get('pk')})"}
				},
				status = status.HTTP_404_NOT_FOUND
			)

		serializer = self.get_serializer(obj)

		return response.Response(data = serializer.data, status = status.HTTP_200_OK)


class PaymentInfoAPIView(views.APIView):
	@extend_schema(
		methods=["GET"],
		auth=None,
		responses = {
			404: ResponseError, 
			200: serializers.PaymentInfoResponse
		},
		parameters=[
			OpenApiParameter(
                name="pk",
                type=int,
                location=OpenApiParameter.PATH,
                description="Search PaymentInfo by ID"
            )
		]
	)
	def get(self, request, pk:int = None):
		payment_info = models.PaymentInfo.objects.filter(
			school_id = pk
		).order_by('-id').first()
		
		if not payment_info:

			return response.Response(
				ResponseError(
					errors=[
						{"message": "No existe información sobre esta escuela"}
					]
				).model_dump(), 
				status = status.HTTP_404_NOT_FOUND
			)

		de_serializer = serializers.PaymentInfoResponse(payment_info)

		return response.Response(
			data = de_serializer.data,
			status = status.HTTP_200_OK
		)


class ContactInfoAPIView(generics.ListAPIView):
	queryset = models.ContactInfo.objects.all()
	serializer_class = serializers.ContactInfoResponse
	pagination_class = paginations.BasicPaginate


	def get_queryset(self):
		return self.queryset.filter(
			school_id = self.kwargs.get("pk")
		).order_by("id")


class ExtraActivityListAPIView(generics.ListAPIView):
	queryset = models.ExtraActivity.objects.all()
	serializer_class = serializers.ExtraActivityListResponse
	pagination_class = paginations.BasicPaginate

	def get_queryset(self):
		return self.queryset.prefetch_related(
			"photos", "schedules"
		).filter(
			school_id = self.kwargs.get("pk")
		).order_by("-created", "-updated")


class ExtraActivityDetailAPIView(generics.RetrieveAPIView):
	queryset = models.ExtraActivity.objects.all()
	serializer_class = serializers.ExtraActivityDetailResponse

	def get_object(self):
		try:
			return self.queryset.prefetch_related(
				"schedules", "files", "photos"
			).select_related(
				"school"
			).get(pk = self.kwargs.get("pk"))
		except models.ExtraActivitie.DoesNotExist as e:
			return None


	def retrieve(self, request, *args, **kwargs):
		obj = self.get_object()

		if not obj:
			return response.Response(
				data = {
					"error": {"message": f"No existe alguna actividad extracurricular con este id ({kwargs.get('pk')})"}
				},
				status = status.HTTP_404_NOT_FOUND
			)

		serializer = self.get_serializer(obj)

		return response.Response(data = serializer.data, status = status.HTTP_200_OK)