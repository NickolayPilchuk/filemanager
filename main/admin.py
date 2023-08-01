from django.contrib import admin
from main.models import Files,Comments,UserExtended,Requests
# Register your models here.
admin.site.register(Files)
admin.site.register(Comments)
admin.site.register(UserExtended)
admin.site.register(Requests)