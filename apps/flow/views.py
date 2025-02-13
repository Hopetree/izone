from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'flow/index.html')

def create(request):
    return render(request, 'flow/create.html')

def edit(request):
    return render(request, 'flow/edit.html')

def view(request):
    return render(request, 'flow/view.html')
