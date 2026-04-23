from django.contrib.auth.models import Permission
from rest_framework.validators import UniqueValidator

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.school.apiv1 import serializers as school_serializers

from apps.user import models as user_models

from apps.management import models as admin_models
from apps.management.commands import commands_admin_user

SCHOOL_HEADER = "X-School-Subdomain"

REQUIRED_PASSWORD_CONFIRM = "Debe enviar un password de confirmación"
REQUIRED_EMAIL = "Debe enviar un email para el usuario"
REQUIRED_PASSWORD = "Debe enviar un password"
REQUIRED_NAME = "Debe enviar un nombre para el usuario"
MIN_LEN_NAME = "El nombre es muy corto"
MAX_LEN_NAME = "El nombre de usuario es muy largo"
MIN_LEN_PASSWORD = "La contraseña es muy corta"
EMAIL_ALREADY_REGISTERED = "Ya existe un usuario con este email"
PASSWORDS_NOT_MATCH = "Las contraseñas no coinciden"

SCHOOL_SUBDOMAIN_DOES_NOT_EXIST = "No existe registro de alguna escuela con este 'subdominio'"


def get_context_request_header(context) -> str | None:
    request = context.get("request")
    return request.headers.get(SCHOOL_HEADER)


class AdminCreateUserSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(
        style={
            "input_type":"password"
        }, 
        write_only = True,
        required = False
    )
    
    class Meta:
        model = user_models.User
        fields = [
            "name",
            "email",
            "password",
            "password_confirm",
        ]
        extra_kwargs = {
            "email":{
                "validators": [
                    UniqueValidator(
                        queryset = user_models.User.objects.all(),
                        message = EMAIL_ALREADY_REGISTERED
                    )
                ],
                "error_messages": {
                    'required': REQUIRED_EMAIL,
                }
            },
            "password": {
                "min_length": user_models.MIN_LENGTH_PASSWORD,
                "error_messages": {
                    'required': REQUIRED_PASSWORD,
                    'min_length': MIN_LEN_PASSWORD
                }
            },
            "name": {
                "required": True,
                "max_length": user_models.MAX_LENGTH_NAME,
                "min_length": user_models.MIN_LENGTH_NAME,

                "error_messages": {
                    'max_length': MAX_LEN_NAME,
                    'min_length': MIN_LEN_NAME,
                    'required': REQUIRED_NAME,
                }
            }
        }
    
    def validate(self, data):

        school_subdomain = get_context_request_header(self.context)

        if not school_subdomain:
            raise serializers.ValidationError(
                {"detail": f"El encabezado [{SCHOOL_HEADER}] es requerido."}
            )
        
        exist = commands_admin_user.school_by_subdomain_exist(
            school_subdomain = school_subdomain
        ).query

        if not exist:
            raise serializers.ValidationError(
                SCHOOL_SUBDOMAIN_DOES_NOT_EXIST,
                code = "does-not-exist"
            )

        password = data.get("password")
        password_confirm = data.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError(PASSWORDS_NOT_MATCH)

        return data

    def create(self, validate_data):

        school_subdomain = get_context_request_header(self.context)

        command = commands_admin_user.add_admin_user_to_school(
            user = validate_data,
            school_subdomain = school_subdomain
        )

        return command.query


class MUserCreateResponse(serializers.ModelSerializer):
    school = serializers.SerializerMethodField()

    class Meta:
        model = user_models.User
        fields = [
            "id", 
            "name", 
            "email", 
            "role",
            "school"
        ]

    def get_school(self, obj):
        school_subdomain = get_context_request_header(self.context)

        return {
            "subdomain": school_subdomain
        }


class UserUpdateRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.User
        fields = ["role"]


class UserPermissionsSerializer(serializers.Serializer):
    permissions = serializers.ListField(child = serializers.CharField())


    def validate_permissions(self, value):
        if not value:
            raise serializers.ValidationError("Debe indicar que permisos desea agregar al usuario")
        
        exists_permissions = Permission.objects.filter(codename__in = value)

        if not exists_permissions:
            raise serializers.ValidationError("No existe ningún permiso con alguno de esos nombres")
        
        return value


class MUserResposeSerializer(serializers.ModelSerializer):
    user_permissions = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='codename'
    )

    class Meta:
        model = user_models.User
        fields = [
            "id", 
            "name", 
            "email", 
            "role", 
            "last_login", 
            "date_joined", 
            "is_active",
            "user_permissions"
        ]