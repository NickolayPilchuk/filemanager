from django.shortcuts import render,redirect
from django.views.generic import DetailView,CreateView,UpdateView,ListView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Files,UserExtended,Requests,Comments
from .forms import Storage_form, Settings_form, Comment_form
from django.urls import reverse_lazy,reverse
from django.views.generic.edit import FormMixin
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import FileResponse
def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserExtended.objects.create(user=User.objects.get(username=form.cleaned_data['username']))
            user =authenticate(request,username=form.cleaned_data['username'],password=form.cleaned_data['password1'])
            if user:
                login(request,user)
                messages.success(request,'Пользователь успешно зарегистрирован')
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
        isblocked = context['viewed_user'] in user_settings.blacklist.all()
        context['isfriend'] = isfriend
        context['isblocked'] = isblocked
        context['viewed_user_settings'] = viewed_user_settings
        context['user_settings'] = user_settings
        return context
@login_required(login_url='login')
def invite(request,user):   #user - тот, кому отправляется приглашение

    target = User.objects.get(username=user)
    if request.user in UserExtended.objects.get(user=target).whitelist.all() or request.user in UserExtended.objects.get(user=target).blacklist.all():
        return redirect('profile', pk=target.id)

    if Requests.objects.filter(from_user=request.user,to=target):
        return redirect('profile', pk=target.id)
    Requests.objects.create(from_user=request.user,to=target)
    messages.success(request,'Запрос успешно отправлен')
    return redirect('profile',pk=target.id)

def accept(request,pk,operation):
    accepted_request = Requests.objects.get(id=pk)
    target_settings = UserExtended.objects.get(user=accepted_request.to)
    viewer_settings = UserExtended.objects.get(user=accepted_request.from_user)
    if accepted_request.to == request.user:
        if operation =='accept':
            target_settings.whitelist.add(accepted_request.from_user)
            viewer_settings.whitelist.add(accepted_request.to)
            target_settings.save()
            viewer_settings.save()
            messages.success(request, 'Запрос успешно принят')
            accepted_request.delete()
        elif operation=='decline':
            accepted_request.delete()
    return redirect('userlists')

@login_required(login_url='login')
def blacklist(request,pk,operation):
    target=User.objects.get(id=pk)
    viewer_settings = UserExtended.objects.get(user=request.user)
    if target in viewer_settings.whitelist.all():
        messages.error(request, 'Нельзя заблокировать пользователя из списка друзей')
        return redirect('profile', pk=pk)
    if operation == 'add':
        viewer_settings.blacklist.add(target)
    else:
        viewer_settings.blacklist.remove(target)
    viewer_settings.save()
    messages.info(request, 'Черный список обновлен')
    return redirect('profile', pk=pk)

@login_required(login_url='login')
def whitelist_delete(request,pk,redirect_to='profile'):
    target = User.objects.get(id=pk)
    target_settings = UserExtended.objects.get(user=target)
    viewer_settings = UserExtended.objects.get(user=request.user)
    viewer_settings.whitelist.remove(target)
    target_settings.whitelist.remove(request.user)
    viewer_settings.save()
    target_settings.save()
    messages.info(request, 'Пользователен удален из списка друзей')
    if redirect_to == 'profile':
        return redirect('profile',pk=pk)
    else:
        return redirect(userlists)
class SearchView(ListView):
    paginate_by = 6
    model = User
    template_name = 'main/search_results.html'
    context_object_name = 'users'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        return context
    def get_queryset(self):
        query = self.request.GET.get("q")
        return User.objects.filter(username__icontains=query)


@login_required(login_url='login')
def my_storage(request):
    if request.method == "POST":
        form = Storage_form(request.POST)
        if form.is_valid():
            viewer_settings = UserExtended.objects.get(user=request.user)
            viewer_settings.storage_status = form.cleaned_data['acces']
            viewer_settings.save()
            messages.info(request, 'Настройки обновлены')
    files = Files.objects.filter(user=request.user)
    p = Paginator(files,9)
    page_number=request.GET.get('page')
    page_obj=p.get_page(page_number)
    status= UserExtended.objects.get(user = request.user).storage_status
    initial = {'acces':status}
    form = Storage_form(initial=initial)
    context = {'form':form,'page':page_obj}
    return render(request,'my_storage.html',context)

def storage(request,pk):
    target_settings = UserExtended.objects.get(user=User.objects.get(id=pk))
    context = {}
    if request.user in target_settings.blacklist.all():
        context['is_allowed'] = False
    if target_settings.storage_status == 'Public' or request.user==User.objects.get(id=pk):
        context['is_allowed'] = True
    elif target_settings.storage_status == 'Closed':
        context['is_allowed'] = False
        return render(request,'main/storage.html',context)
    if target_settings.storage_status == 'Limited':
        if request.user in target_settings.whitelist.all():
            context['is_allowed'] = True
        else:
            context['is_allowed'] = False
            return render(request, 'main/storage.html', context)
    files = Files.objects.filter(user=target_settings.user).exclude(acces='Closed')
    p = Paginator(files, 1)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    context['page'] = page_obj
    context['viewed_user'] = target_settings
    return render(request, 'main/storage.html', context)

@login_required(login_url='login')
def userlists(request):
    friend_requests = Requests.objects.filter(to=request.user)
    viewer_settings = UserExtended.objects.get(user=request.user)
    friends = viewer_settings.whitelist.all()
    blacklist = viewer_settings.blacklist.all()

    friends_paginator=Paginator(friends,4)
    friends_page_number=request.GET.get('page1')
    friends_page=friends_paginator.get_page(friends_page_number)

    blacklist_paginator = Paginator(blacklist, 1)
    blacklist_page_number = request.GET.get('page2')
    blacklist_page = blacklist_paginator.get_page(blacklist_page_number)
    context = {'friend_requests':friend_requests,'blacklist':blacklist_page,'friends':friends_page}
    return render(request,'main/userlists.html',context)

@login_required(login_url='login')
def settings(request):
    viewer_settings = UserExtended.objects.get(user=request.user)
    if request.method == 'POST':
        form = Settings_form(request.POST)
        if form.is_valid():
            viewer_settings.storage_status = form.cleaned_data['acces']
            viewer_settings.save()
            messages.info(request, 'Настройки обновлены')
    status = viewer_settings.storage_status
    initial = {'acces': status}
    form = Settings_form(initial=initial)
    context= {'form':form}
    return render(request,'main/settings.html',context)

class UploadFile(LoginRequiredMixin, CreateView):
    model = Files
    login_url = 'login'
    fields = ['name','description','file','acces']
    def form_valid(self, form):
        instance = form.save(commit = False)
        instance.user = self.request.user
        instance.save()
        messages.info(self.request, 'Файл добавлен')
        return redirect('file',pk=instance.id)

class FileView(FormMixin,DetailView):
    model = Files
    context_object_name = 'file'
    form_class = Comment_form
    def get_success_url(self):
        return reverse('file',args=(self.get_object().pk,))
    def check_acces(self,target_settings,viewer_settings,file):
        if file.acces == 'Public' and not(self.request.user in target_settings.blacklist.all()):
            return True
        if file.acces == 'Closed' and (target_settings!=viewer_settings):
            return False
        if self.request.user in target_settings.whitelist.all() and file.acces== 'Limited':
            return True
        else:
            return False

    def post(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            self.object = self.get_object()
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
        else:
            return redirect('login')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_anonymous:
            if context['file'].acces == 'Public':   #Есть ли доступ для анонимного юзера
                context['allowed'] = True
                context['file'].views+=1
                context['file'].save()
                return context
            else:
                context['allowed'] = False
                return context
        target_settings = UserExtended.objects.get(user=context['file'].user)
        viewer_settings = UserExtended.objects.get(user=self.request.user)
        if self.request.user in target_settings.blacklist.all():
            context['allowed'] = False
            context['owned'] = False
            return context
        comments = Comments.objects.filter(file=context['file'])
        context['form'] = Comment_form()
        p = Paginator(comments,5)
        page_number= self.request.GET.get('page')
        comments_page= p.get_page(page_number)
        context['page'] = comments_page

        if target_settings == viewer_settings:  #Является ли просматривающий файл юзер владельцем
            context['allowed'] = True
            context['owned'] = True
            return context
        context['owned'] = False
        context['allowed'] = self.check_acces(target_settings,viewer_settings,context['file'])
        if context['allowed']:  #Счетчик просмотров
            context['file'].views += 1
            context['file'].save()
        return context

    def form_valid(self, form):
        comment_text = form.cleaned_data['text']
        user = self.request.user
        file = self.get_object()
        Comments.objects.create(text=comment_text,user=user,file=file)
        return super(FileView,self).form_valid(form)

def FileDownload(request,pk):
    file = Files.objects.get(id=pk)
    file_owner = UserExtended.objects.get(user = file.user)
    if request.user == file.user or (file.acces == 'Public') or (file.acces == 'Limited' and request.user in file_owner.whitelist.all()):
        return FileResponse(file.file,as_attachment=True)
class EditFile(UpdateView):
    model = Files
    fields = ['name','description','file','acces']
    template_name = 'main/edit_file.html'

class DeleteFile(DeleteView):
    model = Files
    success_url = reverse_lazy('my_storage')
    template_name = 'main/confirm_delete.html'
    def form_valid(self, form):
        if self.request.user==self.get_context_data()['object'].user:
            messages.success(self.request, "Файл успешно удален")
            return super(DeleteFile,self).form_valid(form)
        else:
            return redirect('home')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allowed'] = self.request.user == context['object'].user    #Доступ разрешен если файл принадлежит пользователю
        return context

@login_required(login_url='login')
def delete_comment(request,pk):
    comment = Comments.objects.get(pk=pk)
    file = comment.file
    if comment.user == request.user or file.user==request.user:
        comment.delete()
        return redirect('file',pk=file.id)
    return redirect('file',pk=file.id)
def homepage(request):
    return render(request,'homepage.html')

def handler404(request,*args,**kwargs):
    response = render('404.html')