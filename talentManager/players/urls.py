from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.top_page, name='top_page'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path("accounts/", include("django.contrib.auth.urls")),
    path('logout/', LogoutView.as_view(next_page='top_page'), name='logout'),
    path('player/records/', views.my_record_list, name='my_record_list'),
    path('player/approve/<int:record_id>/', views.approve_measurement_record, name='approve_measurement_record'),
    path('player/reject/<int:record_id>/', views.reject_measurement_record, name='reject_measurement_record'),
    path('manager/records/', views.measurement_record_list, name='measurement_record_list'),
    path('manager/records/new/', views.create_measurement_record, name='create_measurement_record'),
    path('manager/approvals/', views.approval_status_list, name='approval_status_list'),
    path('all.players.records/', views.all_players_records, name='all_players_records'),
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_create, name='user_create'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('coach/approvals/', views.coach_approval_list, name='coach_approval_list'),
    path('coach/approve/<int:record_id>/', views.approve_record_as_coach, name='approve_record_as_coach'),
    path('coach/reject/<int:record_id>/', views.reject_record_as_coach, name='reject_record_as_coach'),
]
# ここでは、ユーザーのログイン、ログアウト、部員の記録入力、全選手の記録表示、部員管理などのURLパターンを定義しています。