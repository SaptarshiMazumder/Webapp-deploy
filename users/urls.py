
from django.urls import path
from . import views
# from .views import UserRegisterView
# from .views import HomeView
# from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('register/', UserRegisterView.as_view(), name='register'),
    path('register/', views.register, name='register'),
    path('edit_profile/', views.update_user, name='edit-profile'),
    path('login_user', views.login_user, name='login-user'),
    # path('password/', auth_views.PasswordChangeView.as_view(
    #     template_name='registration/change_password.html')),
    path('password/', views.PasswordsChangeView.as_view(
        template_name='registration/change_password.html')),
    path('password_success', views.password_success, name='password-success'),
    path('<int:pk>/profile/', views.profile_page, name='profile-page'),
    path('add_profile/', views.add_profile, name='add-profile'),
    path('<int:pk>/edit_user_profile/', views.edit_user_profile,
         name='edit-user-profile-page'),

]
