from django.urls import path
from .import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', login_required(views.UserLogout.as_view()), name='logout'),
    path('register/', views.UserRegister.as_view(), name='register'),
    path('changepass/', login_required(views.PasswordChange.as_view()), name='change_password'),
    path('profile/', login_required(views.update_profile), name='profile'),
    path('forget-password/', views.ForgetPassword, name="forget_password"),
    path('change-password/<token>/', views.ChangePassword, name="change_password"),
]