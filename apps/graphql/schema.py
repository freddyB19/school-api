import strawberry
from strawberry_django.optimizer import DjangoOptimizerExtension

from .school.querys import SchoolQuery
from .management.querys import AdministratorDetailQuery

@strawberry.type
class Query(AdministratorDetailQuery, SchoolQuery):
	pass

schema = strawberry.Schema(
	query=Query,
	extensions = [DjangoOptimizerExtension]
)
