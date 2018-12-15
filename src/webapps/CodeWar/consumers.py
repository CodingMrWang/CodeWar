from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
import json
from .models import *

state_reference = {"ready": "https://media.giphy.com/media/26BkNrGhy4DKnbD9u/giphy.gif",
                   "preparing": "https://media.giphy.com/media/9g1h1BQx9a55m/giphy.gif", "": "", None: ""}


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.user = self.scope["user"]
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        usernow = self.user
        room_id = self.room_group_name[5:]
        codeUser = CodingUser.objects.get(user=usernow)
        room_instance = Room.objects.get(id=room_id)
        room_owner = room_instance.room_owner
        user1 = room_instance.user1
        user2 = room_instance.user2
        user3 = room_instance.user3
        user4 = room_instance.user4
        if room_instance != None:
            if user2 == None:
                url2 = ""
                state2 = ""
            else:
                url2 = user2.picture.url
                state2 = room_instance.user2_state
            if user3 == None:
                url3 = ""
                state3 = ""
            else:
                url3 = user3.picture.url
                state3 = room_instance.user3_state
            if user4 == None:
                url4 = ""
                state4 = ""
            else:
                url4 = user4.picture.url
                state4 = room_instance.user4_state
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'disconnection_update': "true",
                    'user1_url': user1.picture.url,
                    'user2_url': url2,
                    'user3_url': url3,
                    'user4_url': url4,
                    'user1_status': room_instance.user1_state,
                    'user2_status': state2,
                    'user3_status': state3,
                    'user4_status': state4
                }
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json.get("userstatus"):
            usernow = self.user
            room_id = text_data_json['room_id']
            codeUser = CodingUser.objects.get(user=usernow)
            room_instance = Room.objects.get(id=room_id)
            position = ""
            new_status = ""
            gamestart = "no"
            if room_instance.user4 == codeUser:
                position = 'user4'
                if room_instance.user4_state == 'preparing':
                    room_instance.user4_state = 'ready'
                    new_status = 'ready'
                else:
                    room_instance.user4_state = 'preparing'
                    new_status = 'preparing'
            if room_instance.user3 == codeUser:
                position = 'user3'
                if room_instance.user3_state == 'preparing':
                    room_instance.user3_state = 'ready'
                    new_status = 'ready'
                else:
                    room_instance.user3_state = 'preparing'
                    new_status = 'preparing'
            if room_instance.user2 == codeUser:
                position = 'user2'
                if room_instance.user2_state == 'preparing':
                    room_instance.user2_state = 'ready'
                    new_status = 'ready'
                else:
                    room_instance.user2_state = 'preparing'
                    new_status = 'preparing'
            if room_instance.user1 == codeUser:
                position = 'user1'
                if room_instance.user1_state == 'preparing':
                    room_instance.user1_state = 'ready'
                    new_status = 'ready'
                    gamestart = 'yes'
                else:
                    room_instance.user1_state = 'preparing'
                    new_status = 'preparing'
            room_instance.save()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'position': position,
                    'new_status': new_status,
                    'gamestart': gamestart,
                    'room_id': room_id
                }
            )

        if text_data_json.get("newarrival"):
            usernow = self.user
            room_id = text_data_json['room_id']
            codeUser = CodingUser.objects.get(user=usernow)
            room_instance = Room.objects.get(id=room_id)
            position = ""
            user_url = "/codewar" + codeUser.picture.url
            user_status = 'preparing'
            if room_instance.user1 == codeUser:
                position = 'user1'
            if room_instance.user2 == codeUser:
                position = 'user2'
            if room_instance.user3 == codeUser:
                position = 'user3'
            if room_instance.user4 == codeUser:
                position = 'user4'
                # Send message to room group

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'position': position,
                    'url': user_url,
                    'status': user_status,
                    'newarrival': 'newarrival'
                }
            )
        if text_data_json.get("change"):
            change = text_data_json['change']
            room_id = text_data_json['room_id']

            usernow = self.user

            codeUser = CodingUser.objects.get(user=usernow)
            room_instance = Room.objects.get(id=room_id)
            message = 'nochange'
            initial = ''

            if change == "user2":
                if room_instance.user2 != None:
                    message = "nochange"
                elif room_instance.user3 == codeUser:
                    if room_instance.user3_state == "preparing":
                        message = 'change'
                        initial = 'user3'
                elif room_instance.user4 == codeUser:
                    if room_instance.user4_state == "preparing":
                        message = 'change'
                        initial = 'user4'
            if change == "user3":
                if room_instance.user3 != None:
                    message = "nochange"
                elif room_instance.user2 == codeUser:
                    if room_instance.user2_state == "preparing":
                        message = 'change'
                        initial = 'user2'
                elif room_instance.user4 == codeUser:
                    if room_instance.user4_state == "preparing":
                        message = 'change'
                        initial = 'user4'
            if change == "user4":
                if room_instance.user4 != None:
                    message = "nochange"
                elif room_instance.user3 == codeUser:
                    if room_instance.user3_state == "preparing":
                        message = 'change'
                        initial = 'user3'
                elif room_instance.user2 == codeUser:
                    if room_instance.user2_state == "preparing":
                        message = 'change'
                        initial = 'user2'
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'initial': initial,
                    'modify': change,
                    'room_id': room_id
                }
            )
        if text_data_json.get("exit"):
            usernow = self.user
            room_id = text_data_json['room_id']
            codeUser = CodingUser.objects.get(user=usernow)
            room_instance = Room.objects.get(id=room_id)
            room_owner = room_instance.room_owner
            user_url = codeUser.picture.url
            exit_user = ""
            adjusted_user = ""
            if room_owner == codeUser:
                if room_instance.user2 != None:
                    exit_user = "user1"
                    adjusted_user = "user2"
                elif room_instance.user3 != None:
                    third_user = room_instance.user3
                    room_instance.room_owner = third_user
                    room_instance.user1 = third_user
                    room_instance.user1_state = room_instance.user3_state
                    room_instance.user3 = None
                    room_instance.user3_state = None
                    room_instance.save()
                    exit_user = "user1"
                    adjusted_user = "user3"
                elif room_instance.user4 != None:
                    fourth_user = room_instance.user4
                    room_instance.room_owner = fourth_user
                    room_instance.user1 = fourth_user
                    room_instance.user1_state = room_instance.user4_state
                    room_instance.user4 = None
                    room_instance.user4_state = None
                    room_instance.save()
                    exit_user = "user1"
                    adjusted_user = "user4"
                else:
                    room_instance.delete()
                    # Send message to room group
            if room_instance.user2 == codeUser:
                room_instance.user2 = None
                room_instance.user2_state = ""
                exit_user = "user2"
                adjusted_user = "nouser"
            if room_instance.user3 == codeUser:
                room_instance.user3 = None
                room_instance.user3_state = ""
                exit_user = "user3"
                adjusted_user = "nouser"
            if room_instance.user4 == codeUser:
                room_instance.user4 = None
                room_instance.user4_state = ""
                exit_user = "user4"
                adjusted_user = "nouser"

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'exit_user': exit_user,
                    'adjusted_user': adjusted_user

                }
            )
        if text_data_json.get("room_acces_symbol"):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'room_acces_symbol': text_data_json.get("room_acces_symbol")
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        if event.get('new_status') != None:
            position = event['position']
            new_status = event['new_status']
            room_id = event["room_id"]
            room_instance = Room.objects.get(id=room_id)
            user1_name = room_instance.user1.user.username
            user2_name = ""
            user3_name = ""
            user4_name = ""
            if room_instance.user2:
                user2_name = room_instance.user2.user.username
            if room_instance.user3:
                user3_name = room_instance.user3.user.username
            if room_instance.user4:
                user4_name = room_instance.user4.user.username
            await self.send(text_data=json.dumps({

                'type': 'chat_message',
                'position': position,
                'new_status': new_status,
                "new_status_url": state_reference[new_status],
                'gamestart': event['gamestart'],
                "user1_username": user1_name,
                "user2_username": user2_name,
                "user3_username": user3_name,
                "user4_username": user4_name
            }))
        elif event.get('message') != None:
            message = event['message']
            if message == 'nochange':
                pass
            else:
                room_id = event['room_id']
                room_instance = Room.objects.get(id=room_id)
                initial = event['initial']
                modify = event['modify']
                if modify == "user2":
                    if room_instance.user2 != None:
                        message = 'nochange'
                if modify == "user3":
                    if room_instance.user3 != None:
                        message = 'nochange'
                if modify == "user4":
                    if room_instance.user4 != None:
                        message = 'nochange'
                # Send message to WebSocket
                await self.send(text_data=json.dumps({

                    'type': 'chat_message',
                    'message': message,
                    'initial': initial,
                    'modify': modify

                }))
        elif event.get('newarrival') != None:
            await self.send(text_data=json.dumps({

                'type': 'chat_message',
                'position': event['position'],
                'url': event['url'],
                'status': event['status'],
                'status_url': state_reference[event['status']],
                'newarrival': 'newarrival'
            }))
        elif event.get('exit_user') != None:
            await self.send(text_data=json.dumps({

                'type': 'chat_message',
                'exit_user': event['exit_user'],
                'adjusted_user': event['adjusted_user']
            }))
        elif event.get('disconnection_update') != None:
            await self.send(text_data=json.dumps({

                'type': 'chat_message',
                'disconnection_update': event['disconnection_update'],
                'user1_url': event['user1_url'],
                'user1_status': event['user1_status'],
                'user1_status_url': state_reference[event['user1_status']],
                'user2_url': event['user2_url'],
                'user2_status': event['user2_status'],
                'user2_status_url': state_reference[event['user2_status']],
                'user3_url': event['user3_url'],
                'user3_status': event['user3_status'],
                'user3_status_url': state_reference[event['user3_status']],
                'user4_url': event['user4_url'],
                'user4_status': event['user4_status'],
                'user4_status_url': state_reference[event['user4_status']]
            }))
        elif event.get('room_acces_symbol') != None:
            await self.send(text_data=json.dumps({

                'type': 'chat_message',
                'room_acces_symbol': event['room_acces_symbol']
            }))


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        print("disconnect")
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
