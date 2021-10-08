
from django.urls import path, include
from user import views



urlpatterns = [
    path('register/', views.register, name='user-register'),
    path('login/', views.login, name='user-login'),
    path('logout/', views.logout, name='user-logout'),
    path('accounts/', include('allauth.urls'), name='user-login-auth'),
    path('profile/', views.profile_user, name='user-profile'),
    path('chanels/', views.chanel, name='user-chanel'),
    path('post/', views.post_bai, name='user-post'),
    path('update/', views.update_user, name='update-user'),
]
