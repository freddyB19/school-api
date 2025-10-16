from rest_framework import pagination


class BasicPaginate(pagination.PageNumberPagination):
	page_size = 10
	max_page_size = 20
	page_query_param = "page"
	page_size_query_param = "size"


class CalendarPaginate(pagination.PageNumberPagination):
	page_size = 30
	max_page_size = 50
	page_query_param = "page"
	page_size_query_param = "size"
