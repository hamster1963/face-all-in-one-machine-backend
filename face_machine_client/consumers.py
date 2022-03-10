# chat/consumers.py
import base64
import random

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
import time
from face_machine_client.models import PassInfo, ClientInfo, SyncInfo
from face_irobot_main.models import FaceStore

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


def create_client_id(randomlength=15):
    """
    生成client_id
    """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


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
        self.client_id = create_client_id()
        await self.send(text_data=json.dumps(
            {
                'type': 'init',
                'message': 'connected',
                'error_code': 0,
                'client_id': self.client_id  # 返还client_id,用于判断是否是本次连接
            }))

    async def disconnect(self, close_code):
        await self.send(text_data=json.dumps(
            {
                'message': 'disconnect'
            }))

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        # 登录进程
        if message_type == "authenticate":
            # 设备认证
            client_user = text_data_json.get('client_user')
            client_key = text_data_json.get('client_key')
            if text_data_json.get('client_id') == self.client_id:
                results = await database_sync_to_async(auth_client_token)(client_user, client_key)  # 异步database
                # 登录成功
                if results[0] == 'ok':
                    self.company_id = results[2]
                    await self.send(text_data=json.dumps(
                        {
                            # 返还登录状态与设备参数
                            'message': 'auth_success',
                            'client_token': results[1],
                            'company_id': results[2]
                        }))
                    # TODO 加入到相同企业通信通道中，用于主动下发参数
                    await self.channel_layer.group_add(
                        str(self.company_id),
                        self.channel_name
                    )
                    await self.channel_layer.group_add(
                        str(client_user),
                        self.channel_name
                    )
                # 登录失败
                else:
                    await self.send(text_data=json.dumps(
                        {
                            'message': 'auth_fail'
                        }))
                    await self.close()
            else:
                await self.send(text_data=json.dumps(
                    {
                        'message': 'client_id_error'
                    }))
                await self.close()
        # 通行日志
        elif message_type == "pass_info":
            pass
        # 同步人脸数据库
        elif message_type == "sync_database":
            if self.company_id:
                data_sync_type = text_data_json.get('sync_type')
                # 全同步模式
                if data_sync_type == "full_sync":
                    resp_data = await database_sync_to_async(get_face_store)(self.company_id)
                    await self.send(text_data=json.dumps(resp_data))
                # 检验同步模式
                elif data_sync_type == "check_sync":
                    pass
            else:
                await self.send(text_data=json.dumps(
                    {
                        'message': 'need_auth'
                    }))
        # 同步状态
        elif message_type == "sync_info":
            sync_state = text_data_json.get('sync_state')[0]
            print('sync_state', sync_state)
            if sync_state['type'] == "full_sync":
                pass

    # 向设备下发通知
    async def get_notification(self, event):
        message = event['message']
        # 异步下发
        await self.send(text_data=json.dumps({
            'message': message
        }))


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
        return 'ok', auth.get().client_token, auth.get().client_info.company_id
    else:
        return 'error', None


def create_token():
    """
    生成Token
    """
    token = 'time=' + str(int(time.time())) + 'num=' + str(random.randint(1000, 9999))
    token = base64.b64encode(token.encode('utf-8')).decode('utf-8')
    print('token', token)
    return token


def get_face_store(company_id):
    """
    获取人脸数据库
    """
    resp_data = {
        'type': 'full_sync',
        'face_store': []
    }
    full_store = FaceStore.objects.filter(company_id=company_id)
    for single_face in full_store:
        single_data = {'name': single_face.name,
                       'phone': single_face.phone,
                       'staff_id': single_face.staff_id,
                       'company_id': single_face.company_id,
                       'face_code': str(single_face.face_code)}
        resp_data['face_store'].append(single_data)
    print(len(resp_data['face_store']))
    return resp_data


def update_sync_state(sync_type, sync_state, client_user):
    """
    更新同步状态
    """
    pass
