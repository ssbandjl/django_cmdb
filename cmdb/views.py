from django.shortcuts import HttpResponse

def index(request):
    return HttpResponse("Welcome to XB's HomePage! More about in http:www.logread.cn")