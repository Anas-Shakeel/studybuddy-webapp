from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from .models import Room, Topic, Message
from .forms import RoomForm


# Create your views here.


def login_page(request):
    page = "login"

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user=user)
            return redirect("home")
        else:
            messages.error(request, "Username or password is incorrect")

    return render(request, "base/login_register.html", {"page": page})


def logout_user(request):
    logout(request)
    return redirect("home")


def register_page(request):
    page = "register"
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error occurred during registration")

    return render(request, "base/login_register.html", {"page": page, "form": form})


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
    room_messages = room.message_set.all().order_by("-created")
    participants = room.participants.all()

    if request.method == "POST":
        body = request.POST.get("body", "")
        message = Message.objects.create(user=request.user, room=room, body=body)
        room.participants.add(request.user)
        return redirect("room", pk=room.id)

    context = {
        "room": room,
        "room_messages": room_messages,
        "participants": participants,
    }
    return render(request, "base/room.html", context=context)


@login_required(login_url="/login")
def create_room(request):
    form = RoomForm()

    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")

    return render(request, "base/room_form.html", context={"form": form})


@login_required(login_url="/login")
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("You are not allowed to update this room.")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("home")

    return render(request, "base/room_form.html", context={"form": form})


@login_required(login_url="/login")
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed to delete this room.")

    if request.method == "POST":
        room.delete()
        return redirect("home")

    return render(request, "base/delete.html", context={"obj": room})

@login_required(login_url="/login")
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed to delete this message.")

    if request.method == "POST":
        message.delete()
        return redirect("home")

    return render(request, "base/delete.html", context={"obj": message})
