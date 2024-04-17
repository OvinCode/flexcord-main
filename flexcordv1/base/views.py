from django.shortcuts import render,HttpResponse,redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
from .models import Room,Topic,User,Message
from .forms import RoomForm,UserForm,MyUserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    #search functionality implementation
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    room_count = rooms.count()
    topics = Topic.objects.all()
    context = {'rooms':rooms,'topics':topics,'room_count':room_count}
    return render (request,'base/home.html',context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)


def room(request,pk=id):
    room = Room.objects.get(id=pk)
    context = {'room': room}
    return render (request,'base/room.html',context)

@login_required(login_url='/login') #redirect user to login apge   
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method=='POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        print(request.POST)
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')
          
    context = {'form': form,'topics': topics}
    return render (request,'base/create-room.html',context)

@login_required(login_url='/login')
def updateRoom(request,pk=id):
    room = Room.objects.get(id=pk)
    #passing prefilled datas into roomcreate form
    form = RoomForm(instance=room)

    if request.user != room.host : #to prohibit editing other rooms
        return HttpResponse('You are not allowed here')
    if request.method=='POST':
        form = RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
        
    context = {'form':form}
    return render (request,'base/room-form.html',context)

@login_required(login_url='/login')
def deleteRoom(request,pk=id):
    room = Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()
        return redirect('home')
    
    return render (request,'base/delete.html',{'obj':room})
    

def LoginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)

        except:
            messages.error(request,'User does not exist')

        user = authenticate(request,username=username,password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request,'Username or password does not exist')
        

    context = {'page' : page}

    return render(request,'base/login-register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    form = MyUserCreationForm()
    if request.method =="POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        
        else:
            messages.error(request,"An Error Occured during registration")
        
    context = {'form':form}
    return render(request,'base/login-register.html',context)


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})


@login_required(login_url='/login')
def deleteMessage(request,pk=id):
    message = Message.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed here')

    if request.method == "POST":
        message.delete()
        return redirect('home')
    
    return render (request,'base/delete.html',{'obj':message})


@login_required(login_url='/login')
def userProfile(request,pk=id):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics':topics}
    return render(request,'base/topics.html',context)


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})