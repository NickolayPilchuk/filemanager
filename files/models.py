from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User
# Create your models here.
class Files (models.Model):
    choices = (('Closed','Closed'),
               ('Limited','Limited'),
               ('Public','Public'))
    file = models.FileField(upload_to='media/')
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=300,null=True,blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    acces = models.CharField(max_length=8,choices=choices,default='Closed')
    views = models.IntegerField(default=0)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse("file", kwargs={"pk": self.pk})
    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'
    def delete(self, using=None, keep_parents=False,*args,**kwargs):
        self.file.delete(save=False)
        super(Files,self).delete(*args,**kwargs)

class Comments(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    file = models.ForeignKey(Files,on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username+self.file.name
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
