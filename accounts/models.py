from statistics import mode
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class AdminUser(AbstractUser):

    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+9999999999'. Up to 15 digits allowed."
    )

    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='admin'  
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    email = models.EmailField(unique=True)

    forget_password_token = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username



class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)

    def delete(self):
        self.is_deleted = True
        self.save()
    def restore(self):
        self.is_deleted = False
        self.save()
    class Meta:
        abstract = True
