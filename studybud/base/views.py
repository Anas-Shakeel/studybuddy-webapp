from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Room, Topic
from .forms import RoomForm

# Create your views here.

rooms = [
    {"id": 1, "name": "Let's learn python"},
    {"id": 2, "name": "Design with me"},
    {"id": 3, "name": "Frontend developers"},
]


def home(request):
    q = request.GET.get("q", "")

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )

    topics = Topic.objects.all()
    room_count = rooms.count()

    return render(
        request,
        "base/home.html",
        {"rooms": rooms, "topics": topics, "room_count": room_count},
    )


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
