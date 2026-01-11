from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from .models import *
from .forms import UserRegistration, LoginFormAuthentication, PasswordChangeForm, UserUpdateForm
from django.contrib.auth.views import LoginView, PasswordChangeView, LogoutView
from django.db.models import Q
from .helper import send_forget_password_mail
from django.contrib import messages
import uuid
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model



class UserRegister(CreateView):
    template_name = "accounts/register.html"
    form_class = UserRegistration
    success_url = "/accounts/login/"


class UserLoginView(LoginView):
    form_class = LoginFormAuthentication
    template_name = "accounts/login.html"
    success_url = "/"

    def form_valid(self, form):
        response = super().form_valid(form)
        print("success")
        return redirect(self.success_url)


class PasswordChange(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "accounts/change-password.html"
    success_url = "/accounts/profile/"


def update_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')  
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

class UserLogout(LogoutView):
    template_name = "accounts/profile.html"
    next_page = reverse_lazy('profile')

User = get_user_model()

def ChangePassword(request, token):
    context = {'token_valid': False}
    try:
        user = User.objects.get(forget_password_token=token)
        if user.forget_password_token is None:
            messages.error(request, "This link has already been used or is invalid.")
        else:
            context['token_valid'] = True
            context['user_id'] = user.id

            if request.method == "POST":
                new_password = request.POST.get("new_password")
                confirm_password = request.POST.get("reconfirm_password")
                user_id = request.POST.get("user_id")

                if user_id is None:
                    messages.error(request, "No user id found.")
                    return redirect(f"/accounts/change-password/{token}/")

                if new_password != confirm_password:
                    messages.error(request, "Passwords do not match.")
                    return redirect(f"/accounts/change-password/{token}/")

                user.set_password(new_password)
                user.forget_password_token = None
                user.save()
                messages.success(request, "Your password has been reset successfully")
                return redirect("login")
    except User.DoesNotExist:
        messages.error(request, "Invalid or expired token.")
    except Exception as e:
        print(e)
        messages.error(request, "An error occurred.")
    
    return render(request, "accounts/reset-password.html", context)

def ForgetPassword(request):
    try:
        if request.method == "POST":
            username = request.POST.get("email")
            user_obj = User.objects.filter(Q(email=username) | Q(username=username)).first()

            if not user_obj:
                messages.error(request, "No user found with this username or email.")
                return redirect("forget_password")

            token = str(uuid.uuid4())
            user_obj.forget_password_token = token
            user_obj.save()
            send_forget_password_mail(user_obj.email, token)
            messages.success(request, "An email has been sent.")
            return redirect("login")
    except Exception as e:
        print(e)
        messages.error(request, "An error occurred.")
        return redirect("forget_password")

    return render(request, "accounts/forget-password.html")

