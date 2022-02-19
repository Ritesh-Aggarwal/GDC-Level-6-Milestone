from django.contrib.auth.models import User
from django_filters.rest_framework import (CharFilter, ChoiceFilter,BooleanFilter,
                                           DjangoFilterBackend, FilterSet)
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet

from tasks.models import STATUS_CHOICES, History, Task


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','username']

class TaskSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ["id","title","description","completed","status","user"]

class HistorySerializer(ModelSerializer):

    class Meta:
        model=History
        fields = ['id','task','old_status','new_status','updated_at']



class TaskFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    status = ChoiceFilter(choices=STATUS_CHOICES)
    completed = BooleanFilter()

class HistoryViewSet(ReadOnlyModelViewSet):
    queryset = History.objects.all()
    serializer_class = HistorySerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        try:
            pk = self.kwargs['api_pk']
        except:
            pk = False
        if pk:
            return History.objects.filter(task__user = self.request.user,task__pk=pk)
        else:
            return History.objects.filter(task__user = self.request.user)

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    permission_classes = (IsAuthenticated,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user,deleted=False)
