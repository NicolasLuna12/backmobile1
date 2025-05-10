from django.urls import path
from appUSERS import views

urlpatterns = [
    path('register/', views.CreateUsuarioView.as_view()),
    path('login/', views.CreateTokenView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('update/', views.UpdateProfileView.as_view(), name='update-profile'),
    path('delete/', views.DeleteProfileView.as_view(), name='delete-profile'),
]

 