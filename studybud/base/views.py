from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
# from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from .models import User, Room, Topic, Message
from .forms import RoomForm, UserForm, MyUserCreationForm


# Create your views here.


def login_page(request):
    page = "login"

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user=user)
            return redirect("home")
        else:
            messages.error(request, "Email or password is incorrect")

    return render(request, "base/login_register.html", {"page": page})


def logout_user(request):
    logout(request)
    return redirect("home")


def register_page(request):
    page = "register"
    form = MyUserCreationForm()

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
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

    topics = Topic.objects.all()[:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    return render(
        request,
        "base/home.html",
        {
            "rooms": rooms,
            "topics": topics,
            "room_count": room_count,
            "room_messages": room_messages,
        },
    )


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
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


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    return render(
        request,
        "base/profile.html",
        {
            "user": user,
            "rooms": rooms,
            "room_messages": room_messages,
            "topics": topics,
        },
    )


@login_required(login_url="/login")
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name", ""),
            description=request.POST.get("description", ""),
        )

        return redirect("home")

    return render(
        request, "base/room_form.html", context={"form": form, "topics": topics}
    )


@login_required(login_url="/login")
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed to update this room.")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()

        return redirect("home")

    return render(
        request,
        "base/room_form.html",
        context={
            "form": form,
            "topics": topics,
            "room": room,
        },
    )


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


@login_required(login_url="/login")
def update_user(request):
    form = UserForm(instance=request.user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("user_profile", pk=request.user.id)

    return render(request, "base/update_user.html", {"form": form})


def topics_page(request):
    q = request.GET.get("q", "")

    topics = Topic.objects.filter(name__icontains=q)
    return render(request, "base/topics.html", {"topics": topics})


def activity_page(request):
    room_messages = Message.objects.all()
    return render(request, "base/activity.html", {"room_messages": room_messages})
