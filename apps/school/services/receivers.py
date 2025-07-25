from django.dispatch import receiver
from django.db.models import signals

from apps.school.models import School
from apps.management.models import Administrator 

@receiver(signals.post_save, sender=School)
def create_administrator_site(sender, instance=None, created=False, **kwargs):
	if created:
		Administrator.objects.create(school = instance)
