from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Location
from .serializers import CheckinCreateSerializer

@login_required
def checkin_page(request):
    return render(request, "checkin/checkin.html")

@method_decorator(login_required, name='dispatch')
class LocationListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    def list(self, request):
        data = list(Location.objects.filter(is_active=True).values("id","name","lat","lng","radius_m"))
        return Response(data)

@method_decorator(login_required, name='dispatch')
class CheckinCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CheckinCreateSerializer
    parser_classes = [MultiPartParser, FormParser]
