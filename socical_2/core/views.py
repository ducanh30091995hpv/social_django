
from django.shortcuts import render
from django.http import HttpRequest,HttpResponse
from django.utils.translation import gettext as _



def index(request):

    return render(request, 'main.html')