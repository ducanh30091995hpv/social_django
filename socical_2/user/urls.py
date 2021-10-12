
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
    path('created_index/', views.create_index_user, name='create-index-user'),
    path('created/', views.create_share_user, name='create-share-user'),
    path('edit_share/<int:id>', views.edit_share_user, name='edit-share-user'),
    path('update_share/<int:id>', views.update_share_user, name='update-share-user'),
    path('delete_share/<int:id>', views.delete_share_user, name='delete-share-user'),
    path('delete_short_ly/<int:id>', views.delete_short_ly, name='delete-short-ly'),
    path('create_short_link/<int:id>', views.create_short_link, name='create-short-link'),
    path('eva_short_link', views.eva_short_link, name='eva-short-link'),
    path('short.ly/<slug:slug>', views.short_ly, name='short-ly'),
    # path('copy_short_ly', views.copy_short_ly, name='copy-short-ly'),
    path('short_link', views.short_link, name='short-link'),
    path('count_view/', views.count_view, name='count-view'),
    path('count_view_short_ly/', views.count_view_short_ly, name='count-view-short-ly'),
    path('real_link', views.real_link, name='real-link'),
]
