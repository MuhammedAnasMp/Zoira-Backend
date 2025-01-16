from django.urls import path
from .views import git_pull

urlpatterns = [
    # Other URLs
    path('git-pull', git_pull, name='git_pull'),
]
