from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.AuthView.as_view()),
    path('getCredentialCreateOptions',
         views.CredentialCreateOptionsView.as_view()),
    path('registerCredential', views.RegisterCredentialView.as_view()),
    path('getCredentialGetOptions', views.CredentialGetOptionsView.as_view()),
    path('verifyAssertion', views.VerifyAssertionView.as_view()),
]
