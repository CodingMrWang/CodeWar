from copy import deepcopy
import configparser
import json
import os
import redis
import random
import subprocess

from django.core.mail import send_mail
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from pymongo import MongoClient

from CodeWar.models import *
from CodeWar.form import *

state_reference = {"ready": "https://media.giphy.com/media/26BkNrGhy4DKnbD9u/giphy.gif",
                   "preparing": "https://media.giphy.com/media/9g1h1BQx9a55m/giphy.gif", "": "", None: ""}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Config = configparser.ConfigParser()
Config.read(BASE_DIR + '/../conf/db.ini')
conf_file = Config.get('dbconf', 'address')
conf = configparser.ConfigParser()
conf.read(conf_file)


@login_required
def home_page(request):
    """
    the home page, to render the community of the game and clean all the rooms that associate with the user
    :param request:
    :return:
    """
    # if current page is follow page, only send following users' post
    user = CodingUser.objects.filter(user=request.user).first()
    # clean the room associate with the user
    checkUser(request.user)
    return render(request, "CodeWar/community.html", {'user': user, 'pic': user.picture})


@login_required
def getUserinfo(request):
    """
    :param request:
    :return:  json response of a user info to be processed in the js file
    """
    user = request.user
    codingUser = CodingUser.objects.get(user=user)
    username = user.username
    photo_url = codingUser.picture
    return JsonResponse({
        'username': username,
        'photo_url': '/media/' + str(photo_url),
        'win': codingUser.game_win,
        'lose': codingUser.game_lose,
        'age': codingUser.age,
        'bio': codingUser.bio,
        'fname': user.first_name,
        'lname': user.last_name,
    })


def getRankings(request):
    """
    :param request:
    :return: the json response to be processed in the js
    """
    userList = []
    userSet = CodingUser.objects.all().order_by('-winning_rate')[:10]
    for each in userSet:
        each_dic = {
            'username': each.user.username,
            'photo_url': '/media/' + str(each.picture),
            'winning_rate': each.winning_rate,
            'des': each.bio,
        }
        userList.append(each_dic)
    return JsonResponse({
        'users': userList
    })


def updateAllRooms(request):
    """
    to update all rooms within the community
    :param request:
    :return: json response to be processed in the js

    """
    roomset = Room.objects.all()
    rooms = []
    for each_room in roomset:
        each_dic = {
            'room_id': each_room.id,
            'room_slogan': each_room.room_slogan,
            'room_status': each_room.room_status
        }
        rooms.append(each_dic)
    return JsonResponse({'rooms': rooms})


def listenInvitation(request):
    """
    this is used in the js for dynamic update in the community.html
    :param request:
    :return:
    """
    usernow = request.user
    codingUser = CodingUser.objects.get(user=usernow)
    invitee_set = invitation.objects.filter(invitee=codingUser)
    output = {}
    if invitee_set.exists():
        invitation_list = []
        for each in invitee_set:
            render_response = {}
            render_response['invitor'] = deepcopy(each.invitor.user.username)
            render_response['message'] = deepcopy(each.message)
            render_response['url'] = deepcopy(each.invitor.picture.url)
            render_response['room_id'] = deepcopy(each.room_id.id)
            render_response['invitation_id'] = deepcopy(each.id)
            invitation_list.append(render_response)
        output['invitation_list'] = invitation_list
        output['response'] = "exist"
    else:
        output['response'] = "nonexist"
    return JsonResponse(output)


@login_required
def createRoom(request):
    """
    :param request:
    :return: redirect to the get new room for further process
    """
    if request.method == "GET":
        return HttpResponse("this method not supported yet")
    elif request.method == "POST":
        usernow = request.user
        codingUser = CodingUser.objects.get(user=usernow)
        room_type = request.POST.get("room_type")
        slogan = request.POST.get("slogan")
        room_status = ""
        if room_type == "private":
            room_status = "private"
        if room_type == "public":
            room_status = "available"
        room_instance = Room.objects.create(room_status=room_status, room_owner=codingUser, room_slogan=slogan,
                                            user1=codingUser, user1_state="preparing")
        room_instance.save()
        room_id = room_instance.id
        return HttpResponseRedirect("/codewar/getNewRoom/" + str(room_id))
        


@login_required
def getNewRoom(request, room_id):
    """
    :param request:
    :param room_id: the room id to be passed
    :return: the room.html to be rendered.
    """
    usernow = request.user
    codingUser = CodingUser.objects.get(user=usernow)
    room_type = Room.objects.get(id=room_id).room_status
    room_instance = Room.objects.get(id=room_id)
    outputstatus = ''
    owner_url = "/codewar" + room_instance.room_owner.picture.url
    owner_state = room_instance.user1_state
    owner_state_url = state_reference[owner_state]
    if room_type == "private":
        outputstatus = "Private Room"
    if room_type == "available":
        outputstatus = "Public Room"
    if room_instance.user1 != codingUser and room_instance.user2 != codingUser and room_instance.user3 != codingUser and room_instance.user4 != codingUser:
        if room_instance.user2 != None:
            if room_instance.user3 != None:
                if room_instance.user4 != None:
                    return HttpResponseRedirect(reverse('home'))
                else:
                    room_instance.user4 = codingUser
                    room_instance.user4_state = 'preparing'
                    room_instance.save()
            else:
                room_instance.user3 = codingUser
                room_instance.user3_state = 'preparing'
                room_instance.save()
        else:
            room_instance.user2 = codingUser
            room_instance.user2_state = 'preparing'
            room_instance.save()

    user1_username = room_instance.user1.user.username
    if room_instance.user2:
        user2_url = "/codewar" + room_instance.user2.picture.url
        user2_state = room_instance.user2_state
        user2_username = room_instance.user2.user.username
    else:
        user2_url = ""
        user2_state = ""
        user2_username = ""
    if room_instance.user3:
        user3_url = "/codewar" + room_instance.user3.picture.url
        user3_state = room_instance.user3_state
        user3_username = room_instance.user3.user.username
    else:
        user3_url = ""
        user3_state = ""
        user3_username = ""
    if room_instance.user4:
        user4_url = "/codewar" + room_instance.user4.picture.url
        user4_state = room_instance.user4_state
        user4_username = room_instance.user4.user.username
    else:
        user4_url = ""
        user4_state = ""
        user4_username = ""
    user2_state_url = state_reference[user2_state]
    user3_state_url = state_reference[user3_state]
    user4_state_url = state_reference[user4_state]
    context = {"user1_username": user1_username, "user2_username": user2_username, "user3_username": user3_username,
               "user4_username": user4_username, "personal_url": codingUser.picture.url,
               "personal_username": usernow.username, "room_status": outputstatus, "owner_url": owner_url,
               "owner_state": owner_state,
               "owner_state_url": owner_state_url, "user2_url": user2_url, "user2_state": user2_state,
               "user2_state_url": user2_state_url, "user3_url": user3_url, "user3_state": user3_state,
               "user3_state_url": user3_state_url, "user4_url": user4_url, "user4_state": user4_state,
               "user4_state_url": user4_state_url, 'room_id': room_id}
    return render(request, 'CodeWar/room.html', context, RequestContext(request))


@login_required
def acceptRoom(request):
    """
    :param request:
    :return: the rendered html for the room.html
    """
    if request.method == "GET":
        return HttpResponse("this method not supported yet")
    elif request.method == "POST":
        print(request.POST)
        usernow = request.user
        codingUser = CodingUser.objects.get(user=usernow)
        room_id = request.POST.get("room_id")
        room_instance = Room.objects.get(id=room_id)
        thisInvitation = invitation.objects.filter(invitee=codingUser, room_id=room_instance).first()
        outputstatus = room_instance.room_status
        owner_url = "/codewar" + room_instance.room_owner.picture.url
        owner_state = room_instance.user1_state
        owner_state_url = state_reference[owner_state]
        if room_instance.user1 != codingUser and room_instance.user2 != codingUser and room_instance.user3 != codingUser and room_instance.user4 != codingUser:
            if room_instance.user2 != None:
                if room_instance.user3 != None:
                    if room_instance.user4 != None:
                        return HttpResponseRedirect(reverse('home'))
                    else:
                        room_instance.user4 = codingUser
                        room_instance.user4_state = 'preparing'
                        room_instance.save()
                else:
                    room_instance.user3 = codingUser
                    room_instance.user3_state = 'preparing'
                    room_instance.save()
            else:
                room_instance.user2 = codingUser
                room_instance.user2_state = 'preparing'
                room_instance.save()

        user1_username = room_instance.user1.user.username
        if room_instance.user2:
            user2_url = "/codewar" + room_instance.user2.picture.url
            user2_state = room_instance.user2_state
            user2_username = room_instance.user2.user.username
        else:
            user2_url = ""
            user2_state = ""
            user2_username = ""
        if room_instance.user3:
            user3_url = "/codewar" + room_instance.user3.picture.url
            user3_state = room_instance.user3_state
            user3_username = room_instance.user3.user.username
        else:
            user3_url = ""
            user3_state = ""
            user3_username = ""
        if room_instance.user4:
            user4_url = "/codewar" + room_instance.user4.picture.url
            user4_state = room_instance.user4_state
            user4_username = room_instance.user4.user.username
        else:
            user4_url = ""
            user4_state = ""
            user4_username = ""
        user2_state_url = state_reference[user2_state]
        user3_state_url = state_reference[user3_state]
        user4_state_url = state_reference[user4_state]
        if thisInvitation:
            thisInvitation.delete()
        context = {"user1_username": user1_username, "user2_username": user2_username, "user3_username": user3_username,
                   "user4_username": user4_username, "personal_url": codingUser.picture.url,
                   "personal_username": usernow.username, "room_status": outputstatus, "owner_url": owner_url,
                   "owner_state": owner_state, "owner_state_url": owner_state_url, "user2_url": user2_url,
                   "user2_state": user2_state, "user2_state_url": user2_state_url, "user3_url": user3_url,
                   "user3_state": user3_state, "user3_state_url": user3_state_url, "user4_url": user4_url,
                   "user4_state": user4_state, "user4_state_url": user4_state_url, 'room_id': room_id}
        return render_to_response('CodeWar/room.html', context, RequestContext(request))


def searchUser(request):
    """
    :param request:
    :return: search the user indicated
    """
    search_term = request.POST.get("search_term")
    search_users = User.objects.filter(username__contains=search_term)
    output_list = []
    for each in search_users:
        each_dic = {
            "username": each.username,
            "photo_url": CodingUser.objects.get(user=each).picture.url
        }
        output_list.append(each_dic)
    return JsonResponse({"users": output_list})


@login_required
def createInvitation(request):
    """
    :param request:
    :return: the json response
    """
    if request.method == 'GET':
        return HttpResponse('none')
    if request.method == 'POST':
        invitee_name = request.POST.get('invitee')
        message = request.POST.get('messgae')
        invitor_user = request.user
        invitee_user = User.objects.get(username=invitee_name)
        roomid = request.POST.get('room-id')
        theroom = Room.objects.get(id=roomid)
        invitor = CodingUser.objects.get(user=invitor_user)
        invitee = CodingUser.objects.get(user=invitee_user)
        invitation_created = invitation.objects.create(room_id=theroom, invitor=invitor, invitee=invitee,
                                                       message=message, state="unlistened")
        invitation_created.save()
        return JsonResponse({'response': "created"})


@login_required
def deleteInvitation(request):
    """
    :param request:
    :return: the json response for instruction in the js
    """

    to_delete = request.POST.get("invitation_id")
    delete_object = invitation.objects.get(id=to_delete)
    delete_object.delete()
    return JsonResponse({'response': 'successfully deleted.'})


@login_required
def changeRoomStatus(request):
    """
    :param request:
    :return: json response for indication in the room....
    """
    room_id = request.POST.get('room_id')
    theRoom = Room.objects.get(id=room_id)
    status = theRoom.room_status
    if status == "occupied":
        return JsonResponse({'response': 'nochange'})
    if status == "private":
        theRoom.room_status = "available"
        theRoom.save()
        return JsonResponse({'response': 'topublic'})
    if status == "available":
        theRoom.room_status = "private"
        theRoom.save()
        return JsonResponse({'response': 'toprivate'})


@login_required
def getInRoom(request, roomInfo):
    """
      this is used in the community if the user want to click the 'get in room' button
    :param request:
    :param roomInfo:  roominfo mean the the "Room xxx" for the room id ...
    :return:
    """
    usernow = request.user
    codingUser = CodingUser.objects.get(user=usernow)
    room_id = roomInfo.replace('Room ', '').strip()
    room_instance = Room.objects.get(id=room_id)
    outputstatus = room_instance.room_status
    owner_url = "/codewar" + room_instance.room_owner.picture.url
    owner_state = room_instance.user1_state
    owner_state_url = state_reference[owner_state]
    if room_instance.user1 != codingUser and room_instance.user2 != codingUser and room_instance.user3 != codingUser and room_instance.user4 != codingUser:
        if room_instance.user2 != None:
            if room_instance.user3 != None:
                if room_instance.user4 != None:
                    return HttpResponseRedirect(reverse('home'))
                else:
                    room_instance.user4 = codingUser
                    room_instance.user4_state = 'preparing'
                    room_instance.save()
            else:
                room_instance.user3 = codingUser
                room_instance.user3_state = 'preparing'
                room_instance.save()
        else:
            room_instance.user2 = codingUser
            room_instance.user2_state = 'preparing'
            room_instance.save()

    user1_username = room_instance.user1.user.username
    if room_instance.user2:
        user2_url = "/codewar" + room_instance.user2.picture.url
        user2_state = room_instance.user2_state
        user2_username = room_instance.user2.user.username
    else:
        user2_url = ""
        user2_state = ""
        user2_username = ""
    if room_instance.user3:
        user3_url = "/codewar" + room_instance.user3.picture.url
        user3_state = room_instance.user3_state
        user3_username = room_instance.user3.user.username
    else:
        user3_url = ""
        user3_state = ""
        user3_username = ""
    if room_instance.user4:
        user4_url = "/codewar" + room_instance.user4.picture.url
        user4_state = room_instance.user4_state
        user4_username = room_instance.user4.user.username
    else:
        user4_url = ""
        user4_state = ""
        user4_username = ""
    user2_state_url = state_reference[user2_state]
    user3_state_url = state_reference[user3_state]
    user4_state_url = state_reference[user4_state]
    context = {"user1_username": user1_username, "user2_username": user2_username, "user3_username": user3_username,
               "user4_username": user4_username, "personal_url": codingUser.picture.url,
               "personal_username": usernow.username, "room_status": outputstatus, "owner_url": owner_url,
               "owner_state": owner_state, "owner_state_url": owner_state_url, "user2_url": user2_url,
               "user2_state": user2_state, "user2_state_url": user2_state_url, "user3_url": user3_url,
               "user3_state": user3_state, "user3_state_url": user3_state_url, "user4_url": user4_url,
               "user4_state": user4_state, "user4_state_url": user4_state_url, 'room_id': room_id}
    return render(request, 'CodeWar/room.html', context, RequestContext(request))


@login_required
def updatePosition(request, room_id):
    """
      Called by js file to dynamically update the information within the room , including the position and the state .....
    :param request:
    :param room_id: the room id to be received
    :return:
    """
    usernow = request.user
    codingUser = CodingUser.objects.get(user=usernow)
    room_instance = Room.objects.get(id=room_id)
    outputstatus = room_instance.room_status
    owner_url = "/codewar" + room_instance.room_owner.picture.url
    owner_state = room_instance.user1_state
    owner_state_url = state_reference[owner_state]
    user1_username = room_instance.user1.user.username
    count = 1
    ## get each user information within the room .....
    if room_instance.user2:
        user2_url = "/codewar" + room_instance.user2.picture.url
        user2_state = room_instance.user2_state
        user2_username = room_instance.user2.user.username
    else:
        user2_url = ""
        user2_state = ""
        user2_username = ""
    if room_instance.user3:
        user3_url = "/codewar" + room_instance.user3.picture.url
        user3_state = room_instance.user3_state
        user3_username = room_instance.user3.user.username
    else:
        user3_url = ""
        user3_state = ""
        user3_username = ""
    if room_instance.user4:
        user4_url = "/codewar" + room_instance.user4.picture.url
        user4_state = room_instance.user4_state
        user4_username = room_instance.user4.user.username
    else:
        user4_url = ""
        user4_state = ""
        user4_username = ""
    user2_state_url = state_reference[user2_state]
    user3_state_url = state_reference[user3_state]
    user4_state_url = state_reference[user4_state]
    context = {"user1_username": user1_username, "user2_username": user2_username, "user3_username": user3_username,
               "user4_username": user4_username, "personal_url": codingUser.picture.url,
               "personal_username": usernow.username, "room_status": outputstatus, "owner_url": owner_url,
               "owner_state": owner_state, "owner_state_url": owner_state_url, "user2_url": user2_url,
               "user2_state": user2_state, "user2_state_url": user2_state_url, "user3_url": user3_url,
               "user3_state": user3_state, "user3_state_url": user3_state_url, "user4_url": user4_url,
               "user4_state": user4_state, "user4_state_url": user4_state_url, 'room_id': room_id}
    return JsonResponse(context)


@login_required
def changePosition(request):
    """
        change the position in the room for any user
    """
    modify = request.POST["change"]
    room_id = request.POST["room_id"]
    room_instance = Room.objects.get(id=room_id)
    initial = ""
    ## find the user position for the request user ...
    if room_instance.user2 != None and room_instance.user2.user == request.user:
        initial = "user2"
    elif room_instance.user3 != None and room_instance.user3.user == request.user:
        initial = "user3"
    elif room_instance.user4 != None and room_instance.user4.user == request.user:
        initial = "user4"
    if initial == "":
        return JsonResponse({"response": "no"})

    ## take corresponding action for any specific user ...
    if initial == "user2":
        if modify == "user3":
            temp_user = room_instance.user2
            temp_state = room_instance.user2_state
            if room_instance.user3 != None:
                return JsonResponse({"response": "occupied"})
            room_instance.user3 = temp_user
            room_instance.save()
            room_instance.user3_state = temp_state
            room_instance.user2 = None
            room_instance.user2_state = None
            room_instance.save()
        elif modify == "user4":
            temp_user = room_instance.user2
            temp_state = room_instance.user2_state
            if room_instance.user4 != None:
                return JsonResponse({"response": "occupied"})
            room_instance.user4 = temp_user
            room_instance.save()
            room_instance.user4_state = temp_state
            room_instance.user2 = None
            room_instance.user2_state = None
            room_instance.save()
    elif initial == "user3":
        if modify == "user2":
            temp_user = room_instance.user3
            temp_state = room_instance.user3_state
            if room_instance.user2 != None:
                return JsonResponse({"response": "occupied"})
            room_instance.user2 = temp_user
            room_instance.save()
            room_instance.user2_state = temp_state
            room_instance.user3 = None
            room_instance.user3_state = None
            room_instance.save()
        elif modify == "user4":
            temp_user = room_instance.user3
            temp_state = room_instance.user3_state
            if room_instance.user4 != None:
                return JsonResponse({"response": "occupied"})
            room_instance.user4 = temp_user
            room_instance.save()
            room_instance.user4_state = temp_state
            room_instance.user3 = None
            room_instance.user3_state = None
            room_instance.save()
    elif initial == "user4":
        if modify == "user3":
            temp_user = room_instance.user4
            temp_state = room_instance.user4_state
            if room_instance.user3 != None:
                return JsonResponse({"response": "occupied"})
            room_instance.user3 = temp_user
            room_instance.save()
            room_instance.user3_state = temp_state
            room_instance.user4 = None
            room_instance.user4_state = None
            room_instance.save()
        elif modify == "user2":
            temp_user = room_instance.user4
            temp_state = room_instance.user4_state
            if room_instance.user2 != None:
                return JsonResponse({"response": "occupied"})
            room_instance.user2 = temp_user
            room_instance.save()
            room_instance.user2_state = temp_state
            room_instance.user4 = None
            room_instance.user4_state = None
            room_instance.save()
    room_instance.save()
    return JsonResponse({"response": "success"})


def checkUser(usernow):
    """
     would be used in the home page to check if the user is still in some rooms and remove the room if necessary
     """
    codingUser = CodingUser.objects.get(user=usernow)
    checkset2 = Room.objects.filter(user2=codingUser)
    ## check each position in the room , from user2 to user4
    for each in checkset2:
        each.user2 = None
        each.user2_state = None
        each.save()
    checkset3 = Room.objects.filter(user3=codingUser)
    for each in checkset3:
        each.user3 = None
        each.user3_state = None
        each.save()
    checkset4 = Room.objects.filter(user4=codingUser)
    for each in checkset4:
        each.user4 = None
        each.user4_state = None
        each.save()
    checkset1 = Room.objects.filter(user1=codingUser)
    ## find the query set for the rooms that has the coding user ...
    for each in checkset1:
        if each.user2 == None and each.user3 == None and each.user4 == None:
            each.delete()
        elif each.user2 != None:
            new_owner = each.user2
            new_owner_state = each.user2_state
            each.user2 = None
            each.user2_state = None
            each.room_owner = new_owner
            each.user1 = new_owner
            each.user1_state = new_owner_state
            each.save()

        elif each.user3 != None:
            new_owner = each.user3
            new_owner_state = each.user3_state
            each.user3 = None
            each.user3_state = None
            each.room_owner = new_owner
            each.user1 = new_owner
            each.user1_state = new_owner_state
            each.save()
        elif each.user4 != None:
            new_owner = each.user4
            new_owner_state = each.user4_state
            each.user4 = None
            each.user4_state = None
            each.room_owner = new_owner
            each.user1 = new_owner
            each.user1_state = new_owner_state
            each.save()


def register(request):
    """
    function for user registration
    :param request: request from user
    :return: confirm email info
    """
    try:
        context = {}
        # if get, return register page
        if request.method == 'GET':
            context['form'] = RegistForm()
            return render(request, 'CodeWar/register.html', context)
        # create registForm
        form = RegistForm(request.POST)
        context['form'] = form
        # if form is not valid, return the page
        if not form.is_valid():
            return render(request, 'CodeWar/register.html', context)
        # create a new auth user
        new_user = User(username=form.cleaned_data.get('username'), first_name=form.cleaned_data.get('first_name'),
                        last_name=form.cleaned_data.get('last_name'), email=form.cleaned_data.get('email'))
        new_user.set_password(form.cleaned_data.get('password1'))
        # before email verification, set is_active false
        new_user.is_active = False
        new_user.save()
        # create a external user
        external_user = CodingUser(user=new_user, age=form.cleaned_data.get('age'), bio=form.cleaned_data.get('bio'),
                                   picture='11539038077_.pic.jpg')
        external_user.save()
        context['email'] = form.cleaned_data.get('email')
        # generate a token for external_user
        return confirm_email(request, new_user, context)
    except:
        return redirect(reverse('home'))


def confirm_email(request, new_user, context):
    """
    email confirmation
    :param request: request
    :param new_user: user to check email
    :param context: json
    :return: HttpResponse
    """
    # generate a token
    token = default_token_generator.make_token(new_user)
    email_body = '''
    Welcom to CodeWar. You will have an amazing experience here. Please click the link below to verify your email address and complete the registration of your account:
    http://{}{}'''.format(request.get_host(), reverse('confirm', args=(new_user.username, token)))
    send_mail(subject="Verify your email address", message=email_body, from_email="codingmrwang@gmail.com",
              recipient_list=[new_user.email])
    return HttpResponse(
        "Please click the link we sent to {}, Please click that link to confirm your email address and complete your registation.".format(
            new_user.email))


def activate(request, username, token):
    """
    function to activate a new user
    :param request: request
    :param username: username of the new user
    :param token: token generated by django
    :return: HttpResponse success / fail
    """
    user = User.objects.filter(username=username)
    if user:
        new_user = user.first()
    else:
        return HttpResponse('Activation link is invalid!')
    # if has the user and token is valid, set active true and let user login
    if new_user and default_token_generator.check_token(new_user, token):
        new_user.is_active = True
        new_user.save()
        login(request, new_user)
        return HttpResponse(
            "Thank you for your email confirmation. Now you can login your account. <a href=\"/\">home</a>")
    return HttpResponse('Activation link is invalid!')


@login_required
def start_battle(request, room_name, name_pair):
    """
    allocate two questions and jump to battle page
    :param request: request
    :param room_name: room name of user num + alpha / beta
    :param name_pair: two user a-b
    :return:
    """
    try:
        room_id = int(room_name.split('-')[0])
        teammate = name_pair.split('-')[1]
        client = MongoClient(conf.get('mongo', 'url'))
        db = client.spring
        collection = db.questions
        n = collection.count()
        idx1 = room_id % n
        idx2 = (room_id + 3) % n
        q1 = collection.find().limit(-1).skip(idx1).next()['qid']
        q2 = collection.find().limit(-1).skip(idx2).next()['qid']
        q_list = [q1, q2]

        # allocation different questions for two teammates
        if request.user.username > teammate:
            return battle(request, room_name, name_pair, q_list[0], q_list[1])
        else:
            return battle(request, room_name, name_pair, q_list[1], q_list[0])
    except:
        return redirect(reverse('home'))


@login_required
def battle(request, room_name, name_pair, qid1, qid2):
    """
    start battle, read question from mongodb, display code from redis
    :param request: request
    :param room_name: num-alpha/beta
    :param name_pair: a-b
    :param qid1: question one
    :param qid2: question two
    :return: question info and room, user info.
    """
    try:
        client = MongoClient(conf.get('mongo', 'url'))
        db = client.spring
        collection = db.questions
        q = collection.find_one({"qid": qid1})
        name = q['name']
        des = q['description']
        example = q['Example']
        template = q['template']
        test_cases = q['test_cases'][0]['case']

        r = redis.Redis(host='localhost', port=6379, db=0)
        # username-qid to record code for this question for this user
        if r.get(request.user.username + '-' + qid1):
            template = r.get(request.user.username + '-' + qid1).decode('utf-8')
        key = '{}-{}-score'.format(room_name, qid1)
        # score for this question in this battle roomname-qid-score
        if r.get(key):
            score = 'Score: {}'.format(r.get(key).decode('utf-8'))
        else:
            score = 'Score: 0'

        # chat content in this battle
        chatcontent = r.get('{}-{}-chat'.format(room_name, request.user.username))
        if chatcontent:
            chatcontent = chatcontent.decode('utf-8')
        else:
            chatcontent = ""

        context = {
            'qid': qid1,
            'name': name,
            'des': des,
            'example': example,
            'template': template,
            'test_case': test_cases,
            'room_name_json': mark_safe(json.dumps(room_name)),
            'roomname': room_name,
            'userid': request.user.username,
            'teammate': name_pair.split('-')[1],
            'another': qid2,
            'name_pair': name_pair,
            'score': score,
            "chat": chatcontent
        }
        return render(request, "CodeWar/battle.html", context)
    except:
        return redirect(reverse('home'))


def set_code(request, qid):
    """
    ajax request to save code to redis real-time
    :param request: request
    :param qid: question id
    :return: success
    """
    r = redis.Redis(host='localhost', port=6379, db=0)
    if request.POST.get('code'):
        r.set('{}-{}'.format(request.user.username, qid), request.POST.get('code'))
    return HttpResponse("true")


@login_required
def get_teamate_code(request, uid, qid):
    """
    ajax request to return teammate's code
    :param request: ajax get
    :param uid: teammate uid
    :param qid: question id
    :return: code
    """
    r = redis.Redis(host='localhost', port=6379, db=0)
    return JsonResponse({'code': r.get(uid + '-' + qid).decode('utf-8')})


@login_required
def indi_battle(request):
    """
    individual battle
    :param request: get
    :return: question info and user info
    """
    try:
        client = MongoClient(conf.get('mongo', 'url'))
        db = client.spring
        collection = db.questions
        n = collection.count()
        # random choose questions from collection
        idx = random.sample(range(n), 1)[0]

        q = collection.find().limit(-1).skip(idx).next()

        name = q['name']
        des = q['description']
        example = q['Example']
        template = q['template']
        test_cases = q['test_cases'][0]['case']

        context = {
            'qid': q['qid'],
            'name': name,
            'des': des,
            'example': example,
            'template': template,
            'test_case': test_cases,
        }
        return render(request, "CodeWar/indi-battle.html", context)
    except:
        return redirect(reverse('home'))


@login_required
def get_result(request, qid):
    """
    run the code
    :param request: post
    :param qid: question id
    :return: result
    """
    client = MongoClient(conf.get('mongo', 'url'))
    db = client.spring
    collection = db.questions
    q = collection.find_one({"qid": qid})
    result = []
    count = 0
    # run all cases
    for i in range(0, 6):
        code = request.POST.get('code')
        code += '''\ns = Solution()\nprint(s.{})'''.format(q['test_cases'][i]['func'])
        run = subprocess.Popen(['python3', '-c', code], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=False)
        out, error = run.communicate()
        out = out.decode('utf-8')
        error = error.decode('utf-8')
        case = {}
        if error:
            case['output'] = 'Error'
            case['show'] = error
        elif out.strip() != q['test_cases'][i]['answer']:
            case['output'] = 'wrong answer'
            case['show'] = 'Your output: ' + out
        else:
            case['output'] = 'correct'
            case['show'] = ''
            count += 1
        result.append(case)
    return JsonResponse({'result': result, 'count': count})


@login_required
def get_test_result(request, qid):
    """
    function for run test case
    :param request: post
    :param qid: question id
    :return: result
    """
    client = MongoClient(conf.get('mongo', 'url'))
    db = client.spring
    collection = db.questions
    q = collection.find_one({"qid": qid})
    func_name = q['functionName']
    code = request.POST.get('code')
    test_case = request.POST.get('case')
    commands = test_case.split("\n")

    command = '''\ns = Solution()\nprint(s.{}({}, {}))'''.format(func_name, commands[0], commands[1])
    code += command

    run = subprocess.Popen(['python3', '-c', code], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           shell=False)
    out, error = run.communicate()
    out = out.decode('utf-8')
    error = error.decode('utf-8')
    return JsonResponse({'output': out, 'error': error})


@login_required
def set_score(request, roomname, qid1, qid2):
    """
    set the score for the room if one submit
    :param request: post
    :param roomname: room name
    :param qid1: question one
    :param qid2: question two
    :return: score and if already win battle
    """
    if request.POST.get('score'):
        r = redis.Redis(host='localhost', port=6379, db=0)
        score = 100 * int(request.POST.get('score')) // 6
        r.set('{}-{}-score'.format(roomname, qid1), score)
        # if the score is 100, check if already finish the battle
        if score == 100:
            key2 = '{}-{}-score'.format(roomname, qid2)
            if r.get(key2) and int(r.get(key2).decode('utf-8')) == 100:
                r.set(roomname, 1)
                return JsonResponse({'score': 'Score: {}'.format(score), 'success': 1})
        return JsonResponse({'score': 'Score: {}'.format(score), 'success': 0})
    else:
        return JsonResponse({'score': 'Score: 0', 'success': 0})


@login_required
def clear(request):
    """
    clear all redis records
    :param request:
    :return: HttpResponse
    """
    r = redis.Redis(host='localhost', port=6379, db=0)
    teammate = request.POST.get('teammate')
    qid1 = request.POST.get('qid1')
    qid2 = request.POST.get('qid2')
    roomname = request.POST.get('roomname')

    r.delete('{}-{}-score'.format(roomname, qid1))
    r.delete('{}-{}-score'.format(roomname, qid2))
    r.delete('{}-{}'.format(teammate, qid1))
    r.delete('{}-{}'.format(teammate, qid2))
    r.delete('{}-{}'.format(request.user.username, qid1))
    r.delete('{}-{}'.format(request.user.username, qid2))
    return HttpResponse("finish")


@login_required
def get_score(request, roomname, qid1, qid2):
    """
    function to check score see if already win the battle
    :param request: request
    :param roomname: room name
    :param qid1: question one
    :param qid2: question two
    :return: score and if already win
    """
    r = redis.Redis(host='localhost', port=6379, db=0)
    key = '{}-{}-score'.format(roomname, qid1)
    key2 = '{}-{}-score'.format(roomname, qid2)

    if r.get(key):
        if int(r.get(key).decode('utf-8')) == 100 and r.get(key2) and int(r.get(key2).decode('utf-8')) == 100:
            r.set(roomname, 1)
            return JsonResponse({'score': 'Score: {}'.format(r.get(key).decode('utf-8')), 'success': 1})
        return JsonResponse({'score': 'Score: {}'.format(r.get(key).decode('utf-8')), 'success': 0})
    else:
        return JsonResponse({'score': 'Score: 0', 'success': 0})


@login_required
def getfinalresult(request, roomname):
    """
    check other team's result and see if they have won already
    :param request: request
    :param roomname: roomname
    :return: lose or not
    """
    r = redis.Redis(host='localhost', port=6379, db=0)
    logo = roomname.split('-')[1]

    if logo == 'alpha':
        result = r.get('{}-{}'.format(roomname.split('-')[0], 'beta'))
        if not result:
            return JsonResponse({'success': 0})
        r.delete('{}-{}'.format(roomname.split('-')[0], 'beta'))
        return JsonResponse({'success': result.decode('utf-8')})
    else:
        result = r.get('{}-{}'.format(roomname.split('-')[0], 'alpha'))
        if not result:
            return JsonResponse({'success': 0})
        r.delete('{}-{}'.format(roomname.split('-')[0], 'alpha'))
        return JsonResponse({'success': result.decode('utf-8')})


def loss(request):
    """
    if lose, return lose html
    :param request: request
    :return: lose html
    """
    try:
        codeuser = CodingUser.objects.filter(user=request.user).first()
        # update db
        if codeuser:
            codeuser.game_lose += 1
            codeuser.save()
        context = {}
        return render(request, 'CodeWar/losing.html', context)
    except:
        return redirect(reverse('home'))


def success(request):
    """
    if win, return win html
    :param request: request
    :return: win html
    """
    try:
        codeuser = CodingUser.objects.filter(user=request.user).first()
        # update db
        if codeuser:
            codeuser.game_win += 1
            codeuser.save()
        context = {}
    except:
        return redirect(reverse('home'))
    return render(request, 'CodeWar/winning.html', context)


@login_required
def savechat(request):
    """
    save the chat when jump to another question
    :param request: post
    :return: chat info
    """
    if request.POST:
        r = redis.Redis(host='localhost', port=6379, db=0)
        chat = request.POST.get("chat")
        roomname = request.POST.get("roomname")
        username = request.user.username
        r.set('{}-{}-chat'.format(roomname, username), chat)
    return HttpResponse("success")


@login_required
def edit(request):
    """
    function to edit profile
    :param request: form
    :return: home page
    """
    try:
        username = request.user.username
        user = User.objects.get(username=username)
        user_to_edit = get_object_or_404(User, username=username)
        profile_to_edit = get_object_or_404(CodingUser, user=user)
        # show to forms
        if request.method == 'GET':
            form1 = CodingUserForm(instance=profile_to_edit)
            form2 = UserMetaForm(instance=user_to_edit)
            context = {'form1': form1, 'form2': form2, 'username': username}
            return render(request, 'CodeWar/edit-profile.html', context)
        # if post, save the form
        form1 = CodingUserForm(request.POST, request.FILES, instance=profile_to_edit)
        form2 = UserMetaForm(request.POST, instance=user_to_edit)
        # if not valid, do not save
        if not (form1.is_valid() and form2.is_valid()):
            context = {'form1': form1, 'form2': form2}
            return render(request, 'CodeWar/edit-profile.html', context)
        form1.save()
        form2.save()
        # if password is changed, verify through email
        if form2.cleaned_data.get('password1'):
            user.first_name = form2.cleaned_data.get('first_name')
            user.last_name = form2.cleaned_data.get('last_name')
            user.email = form2.cleaned_data.get('email')
            user.set_password(form2.cleaned_data.get('password1'))
            user.is_active = False
            user.save()
            context = {}
            context['email'] = user.email
            logout(request)
            # logout and send email
            return confirm_email(request, user, context)
        # if did not change password, just login
        login(request, user)
    except:
        return redirect(reverse('home'))
    return redirect(reverse('home'))
