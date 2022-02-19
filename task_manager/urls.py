"""task_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path
from tasks.apiviews import HistoryViewSet, TaskViewSet
from tasks.views import (GenericAllTaskView, GenericCompleteTaskView,
                         GenericCompleteView, GenericListView,
                         GenericTaskCreateView, GenericTaskDeleteView,
                         GenericTaskDetailView, GenericTaskUpdateView,
                         UserCreateView, UserLoginView)
# from rest_framework import routers
from rest_framework_nested import routers
router = routers.SimpleRouter()

# /api route to list all tasks
# route /api/{pk} --> task instance
router.register(r"api",TaskViewSet)

# /historyapi route to list all task's history
router.register(r'historyapi',HistoryViewSet)

# nested route /api/{api_pk}/history/{pk}
# route /api/{api_pk}/history --> history list of task pk
# route /api/{api_pk}/history/{pk} --> history instance
api_router = routers.NestedSimpleRouter(router, r'api', lookup='api')
api_router.register(r'history', HistoryViewSet, basename='api-history')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/signup", UserCreateView.as_view()),
    path("user/login", UserLoginView.as_view()),
    path("user/logout/", LogoutView.as_view()),
    path("tasks/", GenericListView.as_view()),
    path("create-tasks/", GenericTaskCreateView.as_view()),
    path("update-tasks/<pk>", GenericTaskUpdateView.as_view()),
    path("task-details/<pk>", GenericTaskDetailView.as_view()),
    path("delete-task/<pk>", GenericTaskDeleteView.as_view()),
    path("completed_tasks/", GenericCompleteTaskView.as_view()),
    path("all_tasks/", GenericAllTaskView.as_view()),
    path("complete_task/", GenericCompleteView.as_view()),
] + router.urls + api_router.urls
