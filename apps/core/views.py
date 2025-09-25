from django.shortcuts import render
from django.http import HttpResponse

def offline_view(request):
    """Serve offline page for PWA"""
    return render(request, 'offline.html')
