from django.shortcuts import HttpResponse
from django.shortcuts import render

def index(request):
    # return HttpResponse("Welcome to XB's HomePage!\nMore about in http:www.logread.cn")
    return render(request, 'index.html', locals())