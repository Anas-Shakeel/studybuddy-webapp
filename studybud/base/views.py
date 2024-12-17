from django.shortcuts import render, redirect
from .models import Room
from .forms import RoomForm

# Create your views here.

rooms = [
    {"id": 1, "name": "Let's learn python"},
    {"id": 2, "name": "Design with me"},
    {"id": 3, "name": "Frontend developers"},
]


def home(request):
    rooms = Room.objects.all()

    return render(request, "base/home.html", {"rooms": rooms})


def room(request, pk):
    room = Room.objects.get(id=pk)

    context = {"room": room}
    return render(request, "base/room.html", context=context)


def create_room(request):
    form = RoomForm()

    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")

    return render(request, "base/room_form.html", context={"form": form})


def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("home")

    return render(request, "base/room_form.html", context={"form": form})


def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()
        return redirect("home")

    return render(request, "base/delete.html", context={"obj": room})
