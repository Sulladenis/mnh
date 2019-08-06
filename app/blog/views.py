from django.shortcuts import render
from django.views.generic import ListView
from django.core.paginator import Paginator
from blog.models import BlogPhoto, Blog


def index(request):
    post = Blog.objects.get(pk=1)
    imgs = BlogPhoto.objects.filter(post=post)
    return render(request, 'blog/index.html', context={'post': post, 'imgs': imgs})


def bloglist(request):
    post_list = Blog.objects.all()
    paginator = Paginator(post_list, 8)

    page = request.GET.get('page')
    posts = paginator.get_page(page)

    return render(request, 'blog/list.html', {'posts': posts})