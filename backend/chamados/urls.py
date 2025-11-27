from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChamadoViewSet
from .views_sankhya import EmpresasView

router = DefaultRouter()
router.register("chamados", ChamadoViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("sankhya/empresas/", EmpresasView.as_view()),
]