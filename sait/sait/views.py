
from django.shortcuts import render, get_object_or_404
from .models import Trip

def home(request):
    trips = Trip.objects.all()
    return render(request, 'diary/home.html', {'trips': trips})

def trip_detail(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    return render(request, 'diary/trip_detail.html', {'trip': trip})

def travel_map(request):
    return render(request, 'diary/map.html')