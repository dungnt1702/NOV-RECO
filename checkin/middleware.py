from django.http import HttpResponseRedirect
from django.conf import settings
import os

class FaviconMiddleware:
    """
    Middleware to handle favicon.ico requests by redirecting to favicon.png
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for favicon.ico
        if request.path == '/favicon.ico':
            # Redirect to favicon.png
            return HttpResponseRedirect('/static/favicon.png')
        
        response = self.get_response(request)
        return response
