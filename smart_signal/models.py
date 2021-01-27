from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
#class user_profile(AbstractUser):
#   company_name = models.CharField(max_length=200)
#   company_logo = models.ImageField(upload_to='logos')
#   company_logo = models.ImageField(upload_to='logos')

#class Client(AbstractBaseUser):
class Client(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   #user = models.ForeignKey('User',on_delete=models.CASCADE,)
   company_name = models.CharField(max_length=200)
   company_logo = models.ImageField(upload_to='logos')

class Client_details(models.Model):
	cmpny_name = models.CharField(max_length=200)
	#img = models.ImageField(upload_to='pics')
	location = models.CharField(max_length=200)
	signal_at = models.CharField(max_length=200)
#	temp =  models.CharField(max_length=200)

class videos_at(models.Model):
    client_details = models.ForeignKey(Client_details, on_delete=models.CASCADE)
    video_nm= models.CharField(max_length=200)

class signal_details(models.Model):
    cnm = models.CharField(max_length=50)
    signal_name = models.CharField(max_length=200)
    created_on = models.CharField(max_length=11)
    created_at_time = models.CharField(max_length=20,default=99)
    size_of_video = models.IntegerField(default = 0)
    video_title = models.CharField(max_length = 200)
    frequency = models.IntegerField(default = 0)
    subscription_period = models.IntegerField(default = 0)

    def __str__(self):
        return self.cnm +'-' + self.signal_name+'-' + self.video_title+"-"+self.created_on+"-"+self.created_at_time

class db_demo(models.Model):
    nm = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    address =models.CharField(max_length=100)
