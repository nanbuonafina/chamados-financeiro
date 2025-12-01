from django.urls import path
from .views import (
    EmpresasView,
    ParceirosView,
    NaturezasView,
    CentrosResultadoView,
    ProjetosView,
    ProdutosView
)

urlpatterns = [
    path("empresas/", EmpresasView.as_view()),
    path("parceiros/", ParceirosView.as_view()),
    path("naturezas/", NaturezasView.as_view()),
    path("centros-resultado/", CentrosResultadoView.as_view()),
    path("projetos/", ProjetosView.as_view()),
    path("produtos/", ProdutosView.as_view()),
]
