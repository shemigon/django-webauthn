from django.urls import path

from . import views

urlpatterns = [
    path('getCredentialCreateOptions',
         views.CredentialCreateOptionsView.as_view()),
    path('registerCredential', views.RegisterCredentialView.as_view()),
    path('getCredentialGetOptions', views.CredentialGetOptionsView.as_view()),
    path('verifyAssertion', views.VerifyAssertionView.as_view()),
]
