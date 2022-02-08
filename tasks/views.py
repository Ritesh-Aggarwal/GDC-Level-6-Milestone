from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from tasks.forms import CustomLoginForm, CustomUserCreationForm, TaskCreateForm
from tasks.models import Task


# custom class to allow only logged in users and define the queryest accordingly
class AuthorizeLoginUser(LoginRequiredMixin):
    def get_queryset(self):
        tasks = Task.objects.filter(deleted=False,user=self.request.user) 
        return tasks

#signup view
class UserCreateView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "user_create.html"
    success_url = "/user/login"


#login view
class UserLoginView(LoginView,CustomLoginForm):
    form_class = CustomLoginForm
    template_name = "user_login.html"

#create view to add a new task
#NOTE : cascade logic moved to TaskCreateForm as a member function
class GenericTaskCreateView(AuthorizeLoginUser,CreateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_create.html"
    success_url = "/tasks"

    def form_valid(self, form):
        user = self.request.user
        priority =  form.cleaned_data.get("priority")
        form.cascadePriority(user,priority)        
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


#update view of a task 
#NOTE :  updated code to handle cascade priority
class GenericTaskUpdateView(AuthorizeLoginUser,UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_update.html"
    success_url = "/tasks"

    def form_valid(self, form):
        user = self.request.user
        priority =  form.cleaned_data.get("priority")
        form.cascadePriority(user,priority)        
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

#Detail view of a task
class GenericTaskDetailView(AuthorizeLoginUser,DetailView):
    model = Task
    template_name = "task_detail.html"

#Delete view
class GenericTaskDeleteView(AuthorizeLoginUser,DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = '/tasks'
    
# View for viewing pending tasks
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

# View for viewing all task
class GenericAllTaskView(AuthorizeLoginUser,ListView):
    model = Task
    template_name = "all.html"
    context_object_name = "tasks"
    paginate_by = 3

# View for viewing completed task
class GenericCompleteTaskView(LoginRequiredMixin,ListView):
    model = Task
    template_name = "completed.html"
    context_object_name = "tasks"
    paginate_by = 4

    def get_queryset(self):
        tasks = Task.objects.filter(deleted=False,completed=True,user=self.request.user) 
        return tasks

# completed_task route to mark task as completed 
# task_id is a hidden input in the form with value of object.id
# route is csrf protected and also requires user login
class GenericCompleteView(AuthorizeLoginUser,View):
    model = Task
    
    def get(self,request):
        return HttpResponseRedirect("/tasks/")

    def post(self,request):
        task_id = request.POST.get('task_id')
        task = Task.objects.filter(pk=task_id).update(completed=True)
        return HttpResponseRedirect("/tasks/")

