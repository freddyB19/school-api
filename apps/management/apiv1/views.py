from rest_framework import (
	views, 
	status, 
	response, 
	generics
)
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)

from apps.utils.result_commands import ResponseError

from . import serializers

from apps.management.models import Administrator


class AdministratorAPIView(views.APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(
		methods=["GET"],
		auth=None,
		operation_id = "administrator_by_school_id",
		responses = {
			404: ResponseError, 
			200: serializers.AdministratorResponse
		},
		parameters=[
			OpenApiParameter(
                name="school_id",
                type=int,
                location=OpenApiParameter.PATH,
                description="Search 'admins' by school ID"
            )
		]
	)
	def get(self, request, school_id: int = None):
		try:
		
			admin = Administrator.objects.defer("school").prefetch_related(
				"users"
			).get(school_id = school_id)
		
		except Administrator.DoesNotExist as e:
			return response.Response(
				data = {
					"error": {"message": f"No existe información sobre los administradores del portal de un colegio con ID: {school_id}"}
				},
				status = status.HTTP_404_NOT_FOUND
			)

		serializer = serializers.AdministratorResponse(admin)

		return response.Response(
			data = serializer.data,
			status = status.HTTP_200_OK
		)

class AdministratorDetailAPIView(generics.RetrieveAPIView):
	queryset = Administrator.objects.all()
	serializer_class = serializers.AdministratorDetailResponse
	permission_classes = [IsAuthenticated]
	
	def get_object(self):
		try:
			return self.queryset.prefetch_related(
				"users"
			).get(pk = self.kwargs.get("pk"))
		except Administrator.DoesNotExist as e:
			return None
	
	def retrieve(self, request, *args, **kwargs):
		admin = self.get_object()

		if not admin:
			return response.Response(
				data = {
					"error": {"message": f"No existe información sobre los administradores de este portal con ID: {kwargs.get('pk')}"}
				},
				status = status.HTTP_404_NOT_FOUND
			)

		serializer = self.get_serializer(admin)

		return response.Response(
			data = serializer.data,
			status = status.HTTP_200_OK
		)
