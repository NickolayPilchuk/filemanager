from django.shortcuts import render,redirect
from django.views.generic import DetailView,CreateView,UpdateView,ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Files,UserExtended,Requests
# Create your views here.
def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserExtended.objects.create(user=User.objects.get(username=form.cleaned_data['username']))
            user =authenticate(request,username=form.cleaned_data['username'],password=form.cleaned_data['password1'])
            if user:
                login(request,user)
                return redirect(homepage)
    else:
        form = UserCreationForm()
    return render(request,'registration/registration.html',{'form':form})

class ProfileView(LoginRequiredMixin,DetailView):
    login_url = 'login'
    model = User
    context_object_name = 'viewed_user'
    template_name = 'main/user_detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        viewed_user_settings = UserExtended.objects.get(user=context['object'])
        user_settings = UserExtended.objects.get(user=self.request.user)
        isfriend = context['viewed_user'] in user_settings.whitelist.all()
        context['isfriend'] = isfriend
        context['viewed_user_settings'] = viewed_user_settings
        context['user_settings'] = user_settings
        return context
@login_required(login_url='login')
def invite(request,user):   #user - тот, кому отправляется приглашение

    target = User.objects.get(username=user)
    if request.user in UserExtended.objects.get(user=target).whitelist.all():
        return redirect('profile', pk=target.id)

    if Requests.objects.filter(from_user=request.user,to=target):
        return redirect('profile', pk=target.id)
    Requests.objects.create(from_user=request.user,to=target)
    print(user)
    return redirect('profile',pk=target.id)

@login_required(login_url='login')
def userlists(request):
    friend_requests = Requests.objects.filter(to=request.user)
    context = {'friend_requests':friend_requests}
    return render(request,'main/userlists.html',context)

def accept(request,id,operation):
    accepted_request = Requests.objects.get(id=id)
    adressed = UserExtended.objects.get(user=accepted_request.to)
    sender = UserExtended.objects.get(user=accepted_request.from_user)
    if accepted_request.to == request.user:
        if operation == accept:
            adressed.whitelist.add(accepted_request.from_user)
            sender.whitelist.add(accepted_request.to)
            adressed.save()
            sender.save()
        accepted_request.delete()
    return redirect('userlists')

class SearchView(ListView):
    model = User
    template_name = 'main/search_results.html'
    context_object_name = 'users'
    def get_queryset(self):
        query = self.request.GET.get("q")
        return User.objects.filter(username__icontains=query)
@login_required(login_url='login')
def settings(request):
    pass
class UploadFile(LoginRequiredMixin, CreateView):
    model = Files
    login_url = 'login'
    fields = ['name','description','file','acces']
    def form_valid(self, form):
        instance = form.save(commit = False)
        instance.user = self.request.user
        instance.save()
        return redirect('file',pk=instance.id)

@login_required(login_url='login')
def my_storage(request):
    files = Files.objects.filter(user=request.user)
    context = {'files':files,'user' : UserExtended.objects.get(user = request.user)}
    return render(request,'storage.html',context)
# class EditFile(UpdateView): #Доработать
#     model = Files
#     fields = ['name','description','file','acces']
class FileView(DetailView):
    model = Files
    context_object_name = 'file'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_anonymous:
            if context['file'].acces == 'Public':
                context['allowed'] = True
                return context
            else:
                context['allowed'] = False
                return context
        viewed_user = UserExtended.objects.get(user=context['file'].user)
        visitor = UserExtended.objects.get(user=self.request.user)
        if context['file'].acces == 'Public' or (viewed_user == visitor):
            context['allowed']= True
            return context
        if context['file'].acces == 'Closed' and (viewed_user!=visitor):
            context['allowed'] = False
            return context
        if self.request.user in viewed_user.whitelist.all() and context['file'].acces== 'Limited':
            print('хуй')
            context['allowed'] = True
        else:
            context['allowed'] = False

        return context


def homepage(request):
    return render(request,'homepage.html')