from django.urls import path
from django.contrib.auth.views import LoginView,LogoutView
from .views import *
urlpatterns = [
    path('',homepage,name='home'),
    path('my_storage',my_storage,name='my_storage'),
    path('settings',settings,name='settings'),
    path('profile/<pk>',ProfileView.as_view(),name='profile'),
    path('send_invite/<user>',invite,name='invite'),
    path('userlists',userlists,name="userlists"),
    path('accept/<id>/<operation>',accept,name='accept'),
    path('upload',UploadFile.as_view(),name = 'upload'),
    path('search/', SearchView.as_view(), name = 'search_results'),
    path('files/<int:pk>',FileView.as_view(),name = 'file'),
    path('login',LoginView.as_view(redirect_authenticated_user=True,next_page='home'),name='login'),
    path('logout',LogoutView.as_view(next_page='home'),name='logout'),
    path('registration',registration,name='registration')
]