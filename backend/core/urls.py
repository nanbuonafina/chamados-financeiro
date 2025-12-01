from django.contrib import admin
from django.urls import path, include
from auth_microsoft.views import MicrosoftLoginView, MicrosoftCallbackView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("chamados.urls")),
    path('auth/login/microsoft/', MicrosoftLoginView.as_view()),
    path('auth/callback/', MicrosoftCallbackView.as_view()),

]
