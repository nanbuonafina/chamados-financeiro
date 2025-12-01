from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.views import ChamadoViewSet

router = DefaultRouter()
router.register("chamados", ChamadoViewSet)

urlpatterns = [
    path("", include(router.urls)),
]