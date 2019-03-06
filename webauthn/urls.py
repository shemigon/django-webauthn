from django.urls import path

from . import views

app_name = 'webauthn'

urlpatterns = [
    path('credentials/create/',
         views.CredentialCreateOptionsView.as_view(),
         name='credentials-create'),
    path('credentials/register/',
         views.RegisterCredentialView.as_view(),
         name='credentials-register'),
    path('credentials/get/',
         views.CredentialGetOptionsView.as_view(),
         name='credentials-get'),
    path('verify/',
         views.VerifyAssertionView.as_view(),
         name='verify'),
]
