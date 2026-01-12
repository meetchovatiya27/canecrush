from django.contrib import admin
from .models import AdminUser
from .forms import CustomUserCreationForm

class MainAdmin(admin.ModelAdmin):
    form = CustomUserCreationForm
    list_display = ['username', 'email', 'phone_number', 'role']
    fields = ('password', 'username', 'email', 'phone_number', 'address', 'role')
    exclude = ['user_permissions', 'groups', 'last_login', 'date_joined', 'activation_token', 'activation_timestamp', 'password_reset_token', 'password_reset_expire_timestamp', 'password_reset_timestamp']

    def get_form(self, request, obj=None, **kwargs):
        form = super(MainAdmin, self).get_form(request, obj, **kwargs)
        form.request = request
        return form

admin.site.register(AdminUser, MainAdmin)


# Register your models here.
# class UserAdmin(admin.ModelAdmin):
#     class Meta:
#         model = AdminUser
#         list_display = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'role']
#         list_filter = ["role"]