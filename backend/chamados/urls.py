from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChamadoViewSet
from .views_sankhya import ( 
    EmpresasView,
    ParceirosView,
    NaturezasView,
    CentrosResultadoView,
    ProjetosView,
    CentrosResultadoView,
    ProdutosView,
    ParceirosView
)

router = DefaultRouter()
router.register("chamados", ChamadoViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("sankhya/empresas/", EmpresasView.as_view()),
    path("sankhya/parceiros/", ParceirosView.as_view()),
    path("sankhya/naturezas/", NaturezasView.as_view()),
    path("sankhya/centros-resultado/", CentrosResultadoView.as_view()),
    path("sankhya/projetos/", ProjetosView.as_view()),
    path("sankhya/produtos/", ProdutosView.as_view()),
]