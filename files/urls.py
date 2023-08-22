from django.urls import path
from django.contrib.auth.views import LoginView,LogoutView,PasswordChangeView
from django.urls import reverse_lazy
from .views import *


urlpatterns = [
    path('upload',UploadFile.as_view(),name = 'upload'),       #Managing files
    path('<int:pk>',FileView.as_view(),name = 'file'),
    path('edit/<pk>', EditFile.as_view(), name='edit'),
    path('delete/<pk>', DeleteFile.as_view(), name='delete'),   #Delete a file
    path('download/<pk>', FileDownload, name='download'),
    path('delete_comment/<int:pk>', delete_comment,name='delete_comment'),
    ]