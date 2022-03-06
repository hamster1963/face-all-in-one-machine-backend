# chat/consumers.py
import base64
import random

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
import time
from face_machine_client.models import PassInfo, ClientInfo

import string
import random


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class FaceWebsocket(AsyncWebsocketConsumer):
    """
    人脸后台websocket服务
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.client_id = None
        self.company_id = None

    async def connect(self):
        # 初始化连接
        # Join room group
        await self.accept()
        # 生成本次连接的client_id
        self.client_id = self.create_client_id()
        await self.send(text_data=json.dumps(
            {
                'type': 'init',
                'message': 'connected',
                'error_code': 0,
                'client_id': self.client_id
            }))

    async def disconnect(self, close_code):
        await self.send(text_data=json.dumps(
            {
                'message': 'disconnect'
            }))

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        print('text_data_json', text_data_json)
        message_type = text_data_json.get('type')
        print('self.client_id', self.client_id)
        if message_type == "authenticate":
            # 设备认证
            client_user = text_data_json.get('client_user')
            client_key = text_data_json.get('client_key')
            if text_data_json.get('client_id') == self.client_id:
                a = 'hhhh'
            else:
                a = 'shit'
            results = await database_sync_to_async(auth_client_token)(client_user, client_key)
            if results == 'ok':
                await self.send(text_data=json.dumps(
                    {
                        'message': 'okkk' + a
                    }))
        '''message = text_data_json.get('message')  # todo 获取token
        if message:
            self.company_id = message
            # Send message to room group
            await self.channel_layer.group_add(
                self.company_id,
                self.channel_name
            )
            await self.send(
                text_data=json.dumps(
                    {
                        'type': 'chat_message',
                        'message': message
                    })
            )
        else:
            await self.send(
                text_data=json.dumps(
                    {
                        'type': 'wrong',
                        'message': 'wrong_request'
                    })
            )
            await self.close()'''

    def create_client_id(self, randomlength=15):
        """
        生成client_id
        """
        random_str = ''
        base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
        length = len(base_str) - 1
        for i in range(randomlength):
            random_str += base_str[random.randint(0, length)]
        return random_str


def auth_client_token(client_user, client_key):
    """
    设备认证
    """
    auth = ClientInfo.objects.filter(client_user=client_user, client_key=client_key)
    # print('auth', auth)
    auth_state = auth.count()
    # print('auth_state', auth_state)
    if auth_state >= 1:
        auth.update(client_token=create_token())
        return 'ok'
    else:
        return 'error'


def create_token():
    """
    生成Token
    """
    token = 'time=' + str(int(time.time())) + 'num=' + str(random.randint(1000, 9999))
    token = base64.b64encode(token.encode('utf-8')).decode('utf-8')
    print('token', token)
    return token
