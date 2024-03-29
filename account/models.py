from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django.db.models.signals import post_save
from django.dispatch import receiver
from friends.models import FriendList


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not password:
            raise ValueError("Users must have a username")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save()
        return user


def get_profile_image_filepath(self, filename):
    return f"profile_images/{self.pk}/{'profile_image.png'}"


def get_default_profile_image():
    return "static/images/default_profile.png"


class Account(AbstractBaseUser):

    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=120)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    login_now = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    profile_image = models.ImageField(
        max_length=255,
        upload_to=get_profile_image_filepath,
        null=True,
        blank=True,
        default=get_default_profile_image,
    )
    hide_email = models.BooleanField(default=True)

    objects = MyAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username

    def get_profile_image_filename(self):
        return str(self.profile_image)[
            str(self.profile_image).index(f"profile_images/{self.pk}/") :
        ]

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


# Everytime a new user is created a FriendList corresponding to that user is created by using post_save reciever
@receiver(post_save, sender=Account)
def user_save(sender, instance, **kwargs):
    FriendList.objects.get_or_create(user=instance)
