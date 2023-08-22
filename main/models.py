from django.db import models
from django.contrib.auth.models import User
from files.models import Files,Comments
# Create your models here.


class File_Acces(models.Model):
    file = models.OneToOneField(Files,on_delete=models.CASCADE)

class UserExtended(models.Model):
    choices = (('Closed', 'Closed'),
               ('Limited', 'Limited'),
               ('Public', 'Public'))
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    whitelist = models.ManyToManyField(User,related_name='whitelist', blank=True)
    blacklist = models.ManyToManyField(User,related_name='blacklist', blank=True)
    storage_status = models.CharField(max_length=8,choices=choices,default='Closed')
    def __str__(self):
        return self.user.username
class Requests(models.Model):
    from_user = models.ForeignKey(User,related_name='from_user',on_delete=models.CASCADE)
    to = models.ForeignKey(User, related_name='to', on_delete=models.CASCADE)
