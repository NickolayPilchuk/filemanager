from django.shortcuts import redirect
from django.http import FileResponse
from django.urls import reverse_lazy,reverse
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView,CreateView,UpdateView,DeleteView
from .models import Files, Comments
from main.models import UserExtended
from django.contrib import messages
from .forms import Comment_form
from django.core.paginator import Paginator
# Create your views here.
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
