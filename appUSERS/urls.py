from django.urls import path
from appUSERS import views

urlpatterns = [
    path('register/', views.CreateUsuarioView.as_view()),
    path('login/', views.CreateTokenView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('profile/update/', views.RetrieveUpdateUsuarioView.as_view(), name='update_profile'),
    path('profile/delete/', views.DeleteUsuarioView.as_view(), name='delete_profile'),
]

 