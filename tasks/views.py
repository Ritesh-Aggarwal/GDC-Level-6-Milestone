# Add your Views Here
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Avg, Max, Min
from django.forms import ModelForm, ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from tasks.models import Task


class AuthorizeLoginUser(LoginRequiredMixin):
    def get_queryset(self):
        tasks = Task.objects.filter(deleted=False,user=self.request.user) 
        return tasks


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = ' bg-gray-100 rounded-lg p-2'


#signup
class UserCreateView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "user_create.html"
    success_url = "/user/login"

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = ' bg-gray-100 rounded-lg p-2'

#login
class UserLoginView(LoginView,CustomLoginForm):
    form_class = CustomLoginForm
    template_name = "user_login.html"

#modelform
class TaskCreateForm(ModelForm):
    
    def clean_title(self):
        title = self.cleaned_data["title"]
        if(len(title) < 10):
            raise ValidationError("Title is too short")
        return title.upper()
    
    def clean_priority(self):
        p = self.cleaned_data['priority']
        if(p < 1 or p > 10):
            raise ValidationError("Priority should be between 1 and 10")
        return p
    
    class Meta:
        model = Task
        fields = ['title','description','priority','completed']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = ' bg-gray-100 rounded-lg p-2'
        self.fields['description'].widget.attrs['class'] += ' h-44'
        self.fields['completed'].widget.attrs['class'] = 'h-4 w-4 rounded-sm cursor-pointer'

#create view
class GenericTaskCreateView(AuthorizeLoginUser,CreateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_create.html"
    success_url = "/tasks"

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()
        parseDB = Task.objects.filter(deleted=False,completed=False,user=self.request.user,priority__gte=self.object.priority).order_by('priority','-created_date')
        exisitng_priorities = [self.object.priority]
        for t in parseDB[1:]:
            if t.priority in exisitng_priorities:
                t.priority = t.priority+1;
                exisitng_priorities.append(t.priority)
                t.save()
        return HttpResponseRedirect(self.get_success_url())

#deleteview
class GenericTaskDeleteView(AuthorizeLoginUser,DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = '/tasks'

#updateview
class GenericTaskUpdateView(AuthorizeLoginUser,UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_update.html"
    success_url = "/tasks"

#detailview
class GenericTaskDetailView(AuthorizeLoginUser,DetailView):
    model = Task
    template_name = "task_detail.html"

class GenericListView(LoginRequiredMixin,ListView):
    model = Task
    template_name = "index.html"
    context_object_name = "tasks"
    paginate_by = 3

    def get_queryset(self):
        search_term = self.request.GET.get("search")
        tasks = Task.objects.filter(deleted=False, completed=False,user=self.request.user).order_by('priority','-created_date')
        if search_term:
            tasks = tasks.filter(title__icontains=search_term).order_by('priority','-created_date')
        return tasks

class GenericCompleteTaskView(LoginRequiredMixin,ListView):
    model = Task
    template_name = "completed.html"
    context_object_name = "tasks"
    paginate_by = 4

    def get_queryset(self):
        tasks = Task.objects.filter(deleted=False,completed=True,user=self.request.user) 
        return tasks

class GenericAllTaskView(AuthorizeLoginUser,ListView):
    model = Task
    template_name = "all.html"
    context_object_name = "tasks"
    paginate_by = 3


# def complete_task_view(request, index):
#     task = Task.objects.filter(id=index).update(completed=True)
#     return HttpResponseRedirect("/tasks/")

class GenericCompleteView(AuthorizeLoginUser,View):
    model = Task
    
    def get(self,request):
        return HttpResponseRedirect("/tasks/")

    def post(self,request):
        task_id = request.POST.get('task_id')
        task = Task.objects.filter(pk=task_id).update(completed=True)
        return HttpResponseRedirect("/tasks/")

