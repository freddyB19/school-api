from rest_framework import routers

from . import viewsets

router = routers.DefaultRouter()
router.register("school", viewsets.SchoolUpdateVS, basename="school")
router.register("school/news", viewsets.NewsDetailUpdateDeleteVS, basename="news")

