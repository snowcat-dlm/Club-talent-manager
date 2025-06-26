from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.top_page, name='top_page'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path("accounts/", include("django.contrib.auth.urls")),
    path('logout/', LogoutView.as_view(next_page='top_page'), name='logout'),
    path('player/records/', views.player_records, name='player_records'),
    path('manager/input/', views.record_input, name='record_input'),
    path('coach/records/', views.all_players_records, name='all_players_records'),
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_create, name='user_create'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
]