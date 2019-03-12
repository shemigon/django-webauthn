from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('webauthn.urls')),
    path('', views.HomeView.as_view(), name='home'),
    path('logged-in/', views.LoggedInView.as_view(), name='logged-in'),
    path('signed-up/', views.SignedUpView.as_view(), name='signed-up'),
    path('signed-up/complete/', views.SignupCompleteView.as_view(),
         name='signup-complete'),
]
