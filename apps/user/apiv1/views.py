from django.contrib import auth

from rest_framework import (
    status,
    response,
    views,
    generics
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes 

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)

from . import serializers
from .permissions import (
    IsRoleAdminOrReadOnly,
    IsUserOrReadOnly,
    IsValidRequestUpdateUser,
)

from apps.user import models
from apps.user.commands.commands import (
    change_password,
    generate_password,
    get_user_by_email
)

from apps.utils.result_commands import (
    MessageError,
    ResponseSuccess,
    ResponseError
)

from apps.user.utils.token import Token
from apps.user.services.signals.signals import SignalResetPassword


class RegisterAPIView(views.APIView):
    @extend_schema(
        request=serializers.UserRegisterSerializer,
        responses={201: serializers.UserResposeSerializer, 400: MessageError},
        auth=None,
        methods=["POST"],
        operation_id = "user_register"
    )
    def post(self, request, format = None):
                
        serializer_register = serializers.UserRegisterSerializer(
            data = request.data
        )

        if not serializer_register.is_valid():
            return response.Response(
                data = serializer_register.errors, 
                status = status.HTTP_400_BAD_REQUEST
            )
        
        new_user = serializer_register.save()

        de_serializer = serializers.UserResposeSerializer(new_user)

        return response.Response(
            data = de_serializer.data,
            status = status.HTTP_201_CREATED
        )

        
class LoginAPIView(views.APIView):
    @extend_schema(
        request=serializers.LoginSerializer,
        responses={200: serializers.UserResponseLogin, 401: MessageError},
        auth=None,
        methods=["POST"],
        operation_id = "user_login"

    )
    def post(self, request):
        login = serializers.LoginSerializer(data = request.data)

        if not login.is_valid():
            return response.Response(data = login.errors, status = status.HTTP_400_BAD_REQUEST)

        credentials = login.data

        user = auth.authenticate(
            email = credentials['email'], 
            password = credentials['password']
        )

        if not user:
            return response.Response(
                data = {"errors": {"message": "Credenciales invalidas"}},
                status = status.HTTP_401_UNAUTHORIZED
            )
        
        de_serializer = serializers.UserResponseLogin(data = {
            "user": serializers.UserResposeSerializer(user).data,
            "token": Token.get(user = user)
        })

        return response.Response(
            data = de_serializer.initial_data,
            status = status.HTTP_200_OK
        )


class UserAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserResposeSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes.append(IsUserOrReadOnly)
        
        elif self.request.method == "PUT" or self.request.method == "PATCH":
            self.permission_classes.append(
                IsValidRequestUpdateUser
            )
            self.permission_classes.append(IsUserOrReadOnly)

        elif self.request.method == "DELETE":
            
            self.permission_classes.append(IsRoleAdminOrReadOnly)


        return [permission() for permission in self.permission_classes]


class UserUpdatePasswordAPIView(views.APIView):
    permission_classes = [IsAuthenticated, IsUserOrReadOnly]

    @extend_schema(
        request=serializers.UserChangePassword,
        responses={200: ResponseSuccess, 400: MessageError},
        methods=["PATCH"]
    )
    def patch(self, request, pk):

        validate_password = serializers.UserChangePassword(data = request.data)

        if not validate_password.is_valid():
            return response.Response(
                validate_password.errors, 
                status = status.HTTP_400_BAD_REQUEST
            )

        command = change_password(
            pk = pk,
            new_password = validate_password.data['password']
        )

        if not command.status:
            return response.Response(
                data = command.errors, 
                status = status.HTTP_400_BAD_REQUEST
            )

        return response.Response(

            data = ResponseSuccess(
                success = [{"message": "La contraseña se actualizado correctamente"}]
            ).model_dump(),
            status = status.HTTP_200_OK
        )


class UserResetPasswordAPIView(views.APIView):

    @extend_schema(
        methods=["PATCH"],
        request=None,
        responses={
            200: ResponseSuccess, 
            404: ResponseError,
            422: ResponseError
        },
        parameters=[
            OpenApiParameter(
                name="email",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Search user by email"
            )
        ]
    )
    def patch(self, request):
        signal = SignalResetPassword()

        query_email = request.query_params.get("email")
        
        if not query_email:
            return response.Response(
                ResponseError(
                    errors = [
                        {"message": "Debe enviar un valor en el parametro de busqueda: [email]"}
                    ]
                ).model_dump(), 
                status = status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        command = get_user_by_email(email = query_email)

        if not command.status:
            return response.Response(
                data = ResponseError(
                    errors = command.errors
                ).model_dump(), 
                status = status.HTTP_404_NOT_FOUND
            )

        user = command.query

        command_password = generate_password()

        plain_password = command_password.query

        change_password(
            pk = user.id,
            new_password = plain_password
        )

        signal.send(
            plain_password = plain_password,
            name = user.name,
            email = user.email
        )
        
        return response.Response(
            data=ResponseSuccess(
                success = [{"message": "Su contraseña se ha restablecido"}]
            ).model_dump(),
            status = status.HTTP_200_OK
        )