import email
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction
from django.forms import ModelForm, ValidationError

from tasks.models import Task,ReportSchedule

class ReportScheduleForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = ' bg-gray-100 rounded-lg p-2'

    class Meta:
        model = ReportSchedule
        fields = ['email','report_at']


# custom login form class inheriting from AuthenticationForm and add css classes to field using constructor
class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = ' bg-gray-100 rounded-lg p-2'

# custom signup form class inheriting from UserCreationForm and add css classes to field using constructor
class CustomUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = ' bg-gray-100 rounded-lg p-2'

#form for create/update task
class TaskCreateForm(ModelForm):
    
    def clean_title(self):
        title = self.cleaned_data["title"]
        if(len(title) < 5):
            raise ValidationError("Title is too short")
        return title.upper()
    
    def clean_priority(self):
        p = self.cleaned_data['priority']
        if(p < 1 or p > 10):
            raise ValidationError("Priority should be between 1 and 10")      
        return p

    # Logic for cascading same priority
    # UPDATES:using select_for_update to lock rows to avoid concurrency issue
            # using bulk_update to reduce queries
            # instead of iterating though and then checking equality , check if a equal already exist and then iterate
            # check if same priority exists
    def cascade_priority(self,user,priority):
        if Task.objects.filter(deleted=False,completed=False,user=user,priority=priority).exists():
            updateSet = []
            p = priority
            parseDB = Task.objects.select_for_update().filter(deleted=False,completed=False,user=user,priority__gte=priority).order_by('priority')
            with transaction.atomic():
                for task in parseDB:
                    if task.priority == p:
                        task.priority += 1;
                        p += 1
                        updateSet.append(task)
            n = Task.objects.bulk_update(updateSet,['priority'])     

    class Meta:
        model = Task
        fields = ['title','description','priority','completed','status']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = ' bg-gray-100 rounded-lg p-2'
        self.fields['description'].widget.attrs['class'] += ' h-44'
        self.fields['completed'].widget.attrs['class'] = 'h-4 w-4 rounded-sm cursor-pointer'
