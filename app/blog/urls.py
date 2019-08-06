from django.urls import path

from .views import index
from blog.views import  bloglist

urlpatterns = [
    path('detail', index, name='index'),
    path('list', bloglist, name='list'),
] 
