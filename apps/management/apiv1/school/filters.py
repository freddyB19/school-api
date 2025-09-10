import django_filters

from apps.school import models

class NewsFilter(django_filters.FilterSet):
	created_year = django_filters.NumberFilter(
		field_name='created', lookup_expr='year'
	)
	created_month = django_filters.NumberFilter(
			field_name='created', lookup_expr='month'
	)
	created_day = django_filters.NumberFilter(
			field_name='created', lookup_expr='day'
	)

	updated_year = django_filters.NumberFilter(
			field_name='updated', lookup_expr='year'
	)
	updated_month = django_filters.NumberFilter(
			field_name='updated', lookup_expr='month'
	)
	updated_day = django_filters.NumberFilter(
			field_name='updated', lookup_expr='day'
	)

	class Meta:
		model = models.News
		fields = ["created", "updated", "status"]
