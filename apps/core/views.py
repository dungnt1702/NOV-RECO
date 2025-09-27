from django.http import HttpResponse
from django.shortcuts import render


def offline_view(request):
    """Serve offline page for PWA"""
    return render(request, "offline.html")
