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


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
	pass

class OfficeHourFilter(django_filters.FilterSet):
	description = django_filters.CharFilter(
		field_name = "interval_description", lookup_expr = "icontains"
	)
	is_active = django_filters.BooleanFilter(
		field_name="time_group", lookup_expr = 'active' 
	)
	undays = django_filters.BooleanFilter(
		field_name="time_group", lookup_expr = "daysweek__isnull"
	)
	days = NumberInFilter(
		field_name = "time_group", 
		lookup_expr = "daysweek__day__in",
		distinct = True
	)

	class Meta:
		model = models.OfficeHour
		fields = ["interval_description"]


class TimeGroupFilter(django_filters.FilterSet):
	type = django_filters.CharFilter(
		field_name = "type", lookup_expr = "icontains"
	)
	
	is_active = django_filters.BooleanFilter(field_name="active")
	
	days = NumberInFilter(
		field_name = "daysweek", 
		lookup_expr = "day__in",
		distinct = True
	)

	class Meta:
		model = models.TimeGroup
		fields = ["type", "days", "is_active"]



class CalendarFilter(django_filters.FilterSet):
	title = django_filters.CharFilter(
		field_name = "title", lookup_expr = "icontains"
	)
	month = django_filters.NumberFilter(
		field_name='date', lookup_expr='month'
	)

	class Meta:
		model = models.Calendar
		fields = ["month", "title"]