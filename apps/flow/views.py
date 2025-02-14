from django.shortcuts import render
from blog.utils import add_views

# Create your views here.

@add_views('flow:index', '流程设计')
def index(request):
    return render(request, 'flow/index.html')

def create(request):
    return render(request, 'flow/create.html')

def edit(request):
    return render(request, 'flow/edit.html')

def view(request):
    return render(request, 'flow/view.html')
