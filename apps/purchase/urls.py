from django.urls import path
from .utils import git_pull

urlpatterns = [
    path('git-pull', git_pull, name='git_pull'),
]
