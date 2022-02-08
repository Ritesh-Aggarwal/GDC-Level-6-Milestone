from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.forms import ModelForm, ValidationError
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from tasks.models import Task


# custom class to allow only logged in users and define the queryest accordingly
class AuthorizeLoginUser(LoginRequiredMixin):
    def get_queryset(self):
        tasks = Task.objects.filter(deleted=False,user=self.request.user) 
        return tasks

# custom signup form class inheriting from UserCreationForm and add css classes to field using constructor
class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = ' bg-gray-100 rounded-lg p-2'


# custom login form class inheriting from AuthenticationForm and add css classes to field using constructor
class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = ' bg-gray-100 rounded-lg p-2'

#signup view
class UserCreateView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "user_create.html"
    success_url = "/user/login"


#login view
class UserLoginView(LoginView,CustomLoginForm):
    form_class = CustomLoginForm
    template_name = "user_login.html"

#form for create/update task
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

    # NOTE: Logic for cascading same priority
    # UPDATES:using select_for_update to lock rows to avoid concurrency issue
            # using bulk_update to reduce queries
            # using exclude to avoid using slice operation ([1:]) by using pk of current task 
    def cascadePriority(self,user,priority,pk):
        exisitng_priorities = [priority]
        parseDB = Task.objects.select_for_update().filter(deleted=False,completed=False,user=user,priority__gte=priority).exclude(pk=pk).order_by('priority','-created_date')
        with transaction.atomic():
            for i in range(len(parseDB)):
                if parseDB[i].priority in exisitng_priorities:
                    parseDB[i].priority += 1;
                    exisitng_priorities.append(parseDB[i].priority)
        n = Task.objects.bulk_update(parseDB,['priority'])             

    class Meta:
        model = Task
        fields = ['title','description','priority','completed']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = ' bg-gray-100 rounded-lg p-2'
        self.fields['description'].widget.attrs['class'] += ' h-44'
        self.fields['completed'].widget.attrs['class'] = 'h-4 w-4 rounded-sm cursor-pointer'

#create view to add a new task
#NOTE : cascade logic moved to TaskCreateForm as a member function
class GenericTaskCreateView(AuthorizeLoginUser,CreateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_create.html"
    success_url = "/tasks"

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()
        user = self.request.user
        priority = self.object.priority
        pk = self.object.id
        form.cascadePriority(user,priority,pk)        
        return HttpResponseRedirect(self.get_success_url())

#Delete view
class GenericTaskDeleteView(AuthorizeLoginUser,DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = '/tasks'

#update view of a task 
#NOTE :  updated code to handle cascade priority
class GenericTaskUpdateView(AuthorizeLoginUser,UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_update.html"
    success_url = "/tasks"

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()
        user = self.request.user
        priority = self.object.priority
        pk = self.object.id
        form.cascadePriority(user,priority,pk)                
        return HttpResponseRedirect(self.get_success_url())

#Detail view of a task
class GenericTaskDetailView(AuthorizeLoginUser,DetailView):
    model = Task
    template_name = "task_detail.html"

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

