from rest_framework import pagination


class BasicPaginate(pagination.PageNumberPagination):
	page_size = 10
	max_page_size = 20
	page_query_param = "page"
	page_size_query_param = "size"