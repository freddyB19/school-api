
from django.db.models import Prefetch
from django.contrib.auth import get_user_model
import strawberry, strawberry_django


from apps.management import models
from apps.graphql.utils import get_user_from_token

from .types import Response, AdminResponse, AdminErrorResponse, ErrorCode


ERROR_PERMISSION = "permission"

STATUS_CODE_UNAUTHENTICATED = 401
MESSAGE_UNAUTHENTICATED = "El usuario no está autenticado"
CODE_UNAUTHENTICATED = "UNAUTHENTICATED"

STATUS_CODE_WITHOUT_PERMISSION = 403
MESSAGE_WIHTOUT_SCHOOL_PERMISSION = "No tienes permisos para (acceder o modificar) información que no te pertenece"
CODE_PERMISSION_DETAIL = "WITHOUT_SCHOOL_PERMISSION"

@strawberry.type
class AdministratorDetailQuery:
	
	@strawberry_django.field
	def administrator(self, pk: strawberry.ID, info: strawberry.Info) -> Response:
		messages = []
		user = get_user_from_token(info.context.request)
		
		if not user.is_authenticated:
			messages.append(
				AdminErrorResponse(
					kind=ERROR_PERMISSION,
					message=MESSAGE_UNAUTHENTICATED,
					code= ErrorCode(code=CODE_UNAUTHENTICATED, status = STATUS_CODE_UNAUTHENTICATED)
				)
			)
		elif not models.Administrator.objects.filter(pk = pk, users__id = user.id).exists():
			messages.append( 
				AdminErrorResponse(
					kind=ERROR_PERMISSION,
					message=MESSAGE_WIHTOUT_SCHOOL_PERMISSION,
					code= ErrorCode(code=CODE_PERMISSION_DETAIL, status = STATUS_CODE_WITHOUT_PERMISSION)
				)
			)


		if messages:
			return AdminResponse(messages = messages)

		return models.Administrator.objects.select_related(
			"school"
		).prefetch_related(
			Prefetch(
				"users",
				queryset = get_user_model().objects.all()
			)
		).filter(pk = pk, users__id = user.id).first()
