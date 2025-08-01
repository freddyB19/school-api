import graphene

from .school.querys import SchoolQuery
from .management_user.mutations import ManagementUserMutation

class Query(
	SchoolQuery,
	graphene.ObjectType
):
	pass


class Mutation(
	ManagementUserMutation, 
	graphene.ObjectType
):
	pass
	

schema = graphene.Schema(query=Query, mutation = Mutation)