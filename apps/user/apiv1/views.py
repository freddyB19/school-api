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
    extend_schema_view,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes

from . import serializers
from .permissions import (
    IsRoleAdminOrReadOnly,
    IsUserOrReadOnly,
    IsValidRequestUpdateUser,
    AdminCannotChangeOwnRole
)

from apps.user import models
from apps.user.commands.commands import (
    create_user,
    change_password,
    generate_password,
    get_user
)

from apps.utils.result_commands import (
    MessageError,
    ResponseSuccess,
    ResponseError,
    BaseMessage
)

from apps.user.utils.token import Token
from apps.user.services.signals import SignalResetPassword


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
                serializer_register.errors, 
                status = status.HTTP_400_BAD_REQUEST
            )
        
        command = create_user(user = serializer_register.data)

        if not command.status:
            return response.Response(
                data = command.errors, 
                status = status.HTTP_400_BAD_REQUEST
            )

        de_serializer = serializers.UserResposeSerializer(command.query)

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
    permission_classes = [IsAuthenticated, IsUserOrReadOnly]

    @extend_schema(
        responses={
            200: ResponseSuccess, 
            400: ResponseError
        },
        methods=["PATCH"]
    )
    def patch(self, request, pk):
        signal = SignalResetPassword()

        command = get_user(pk = pk)

        if not command.status:
            return response.Response(
                data = ResponseError(
                    errors = command.errors
                ).model_dump(), 
                status = status.HTTP_400_BAD_REQUEST
            )

        user = command.query

        command_password = generate_password()

        plain_password = command_password.query

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



class UserUpdateRoleAPIView(views.APIView):
    permission_classes = [IsAuthenticated, AdminCannotChangeOwnRole]

    @extend_schema(
        methods=["PATCH"],
        request=serializers.UserUpdateRoleSerializer,
        responses={
            200: serializers.UserResposeSerializer,
            404: ResponseError
        },
        operation_id = "user_update_role"
    )
    def patch(self, request, pk):

        validate_role = serializers.UserUpdateRoleSerializer(data = request.data)

        if not validate_role.is_valid():
            return response.Response(
                data = validate_role.errors,
                status = status.HTTP_400_BAD_REQUEST
            )

        command = get_user(pk = pk)

        if not command.status:
            return response.Response(
                data = ResponseError(
                    errors = command.errors
                ).model_dump(), 
                status = status.HTTP_400_BAD_REQUEST
            )

        user = command.query

        user.role = validate_role.data['role']
        user.save()

        return response.Response(
            data = serializers.UserResposeSerializer(user).data,
            status = status.HTTP_200_OK
        )
