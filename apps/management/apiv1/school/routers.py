from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("school", views.SchoolUpdateVS, basename="school")
router.register("news", views.NewsDetailUpdateDeleteVS, basename="news")

