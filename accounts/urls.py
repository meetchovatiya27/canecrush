from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),  # ✅ NO login_required
    path('register/', views.UserRegister.as_view(), name='register'),

    path('profile/', login_required(views.update_profile), name='profile'),
    path('changepass/', login_required(views.PasswordChange.as_view()), name='change_password'),

    path('forget-password/', views.ForgetPassword, name='forget_password'),
    path('reset-password/<token>/', views.ChangePassword, name='reset_password'),
]
