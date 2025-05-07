from django.urls import path
from appUSERS import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', views.CreateUsuarioView.as_view()),
    path('login/', views.CreateTokenView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('update/', views.UpdateProfileView.as_view(), name='update-profile'),
    path('delete/', views.DeleteProfileView.as_view(), name='delete-profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

