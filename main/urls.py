from django.urls import path
from django.contrib.auth.views import LoginView,LogoutView,PasswordChangeView
from django.urls import reverse_lazy
from .views import *
urlpatterns = [
    path('',homepage,name='home'),
    path('search/', SearchView.as_view(), name = 'search_results'),

    path('login',LoginView.as_view(redirect_authenticated_user=True,next_page='home'),name='login'),    #Auth
    path('logout',LogoutView.as_view(next_page='home'),name='logout'),
    path('registration',registration,name='registration'),
    path('change_password',PasswordChangeView.as_view(success_url=reverse_lazy('home')),name='change_password'),

    path('profile/<pk>',ProfileView.as_view(),name='profile'),
    path('my_storage',my_storage,name='my_storage'),
    path('settings',settings,name='settings'),
    path('storage/<pk>',storage,name='storage'),
    path('userlists',userlists,name="userlists"),

    path('upload',UploadFile.as_view(),name = 'upload'),       #Managing files
    path('files/<int:pk>',FileView.as_view(),name = 'file'),
    path('edit/<pk>', EditFile.as_view(), name='edit'),
    path('delete/<pk>', DeleteFile.as_view(), name='delete'),   #Delete a file
    path('download/<pk>', FileDownload, name='download'),

    path('send_invite/<user>',invite,name='invite'),    #Friends & Blacklist
    path('accept/<pk>/<operation>',accept,name='accept'),
    path('delete_user/<pk>/<redirect_to>',whitelist_delete,name='remove'), #Remove user from friendlist
    path('blacklist/<pk>/<operation>',blacklist,name='blacklist'),

    path('delete_comment/<int:pk>', delete_comment,name='delete_comment'),



]