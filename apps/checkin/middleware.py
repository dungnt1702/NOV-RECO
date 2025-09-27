from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class FaviconMiddleware(MiddlewareMixin):
    """
    Middleware để xử lý favicon requests
    """

    def process_request(self, request):
        if request.path == "/favicon.ico":
            return HttpResponse(status=204)  # No content
        return None
