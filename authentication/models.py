# from asyncio.windows_events import NULL
# from asyncio.windows_events import NULL
from datetime import time
from distutils.command.upload import upload
from email.policy import default
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
# def get_upload_file_name(userpic, filename):
#     return u'photos/%s/%s_%s' % (str(userpic.user.id),
#                                  str(time()).replace('.', '_'),
#                                  filename)


class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    trustscore = models.IntegerField(default=0)
    profile_pic = models.ImageField(null=True, blank = True, upload_to="images/profile/")
    fb_url = models.CharField(max_length=255,null=True, blank=True)
    insta_url = models.CharField(max_length=255,null=True, blank=True)
    verified = models.BooleanField(default=False)
     