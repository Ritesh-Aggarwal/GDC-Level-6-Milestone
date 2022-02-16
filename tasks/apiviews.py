from django.contrib.auth.models import User
from django_filters.rest_framework import (CharFilter, ChoiceFilter,
                                           DjangoFilterBackend, FilterSet)
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from tasks.models import STATUS_CHOICES, Task


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','username']

class TaskSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ["title","description","completed","user"]



class TaskFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    status = ChoiceFilter(choices=STATUS_CHOICES)


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
