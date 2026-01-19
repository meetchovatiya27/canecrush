from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, PasswordChangeView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
import uuid

from requests import request

from .models import *
from .forms import (
    UserRegistration,
    LoginFormAuthentication,
    PasswordChangeForm,
    UserUpdateForm
)
from .helper import send_forget_password_mail


User = get_user_model()

# =========================
# USER REGISTRATION
# =========================
class UserRegister(CreateView):
    template_name = "accounts/register.html"
    form_class = UserRegistration
    success_url = "/accounts/login/"


# =========================
# USER LOGIN
# =========================
class UserLoginView(LoginView):
    form_class = LoginFormAuthentication
    template_name = "accounts/login.html"

    def get_success_url(self):
        return "/"


# =========================
# USER LOGOUT
# =========================
class UserLogout(LogoutView):
    next_page = reverse_lazy("login")

    


# =========================
# PASSWORD CHANGE (LOGGED IN)
# =========================
class PasswordChange(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "accounts/change-password.html"
    success_url = reverse_lazy("profile")


# =========================
# UPDATE PROFILE
# =========================
@login_required
def update_profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect("profile")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})


# =========================
# FORGET PASSWORD
# =========================
def ForgetPassword(request):
    if request.method == "POST":
        username = request.POST.get("email")

        user_obj = User.objects.filter(
            Q(email=username) | Q(username=username)
        ).first()

        if not user_obj:
            messages.error(request, "No user found with this email or username.")
            return redirect("forget_password")

        token = str(uuid.uuid4())
        user_obj.forget_password_token = token
        user_obj.save()

        send_forget_password_mail(user_obj.email, token)
        messages.success(request, "Password reset link sent to your email.")
        return redirect("login")

    return render(request, "accounts/forget-password.html")


# =========================
# RESET PASSWORD (TOKEN)
# =========================
def ChangePassword(request, token):
    context = {"token_valid": False}

    try:
        user = User.objects.get(forget_password_token=token)

        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("reconfirm_password")

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect(request.path)

            user.set_password(new_password)
            user.forget_password_token = None
            user.save()

            messages.success(request, "Password reset successfully.")
            return redirect("login")

        context["token_valid"] = True

    except User.DoesNotExist:
        messages.error(request, "Invalid or expired password reset link.")

    return render(request, "accounts/reset-password.html", context)
