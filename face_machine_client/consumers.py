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
        # 初始化参数
        super().__init__(args, kwargs)
        self.client_user = None
        self.client_id = None
        self.company_id = None

    async def connect(self):
        # 初始化连接
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
        # 处理websocket
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        # 登录进程
        if message_type == "authenticate":
            # 设备认证
            client_user = text_data_json.get('client_user')
            client_key = text_data_json.get('client_key')
            # 校验连接是否有效
            if text_data_json.get('client_id') == self.client_id:
                # 异步database
                results = await database_sync_to_async(auth_client_token)(client_user, client_key)
                # 登录成功
                if results[0] == 'ok':
                    self.company_id = results[2]
                    self.client_user = client_user
                    await self.send(text_data=json.dumps(
                        {
                            # 返还登录状态与设备参数
                            'message': 'auth_success',
                            'client_token': results[1],
                            'company_id': results[2]
                        }))
                    # 加入到相同企业通信通道中，用于主动下发参数
                    await self.channel_layer.group_add(
                        str(self.company_id),
                        self.channel_name
                    )
                    # 加入设备单独通信通道，用于点对点下发参数
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
            if self.company_id:
                info_detail = text_data_json.get("info_detail")
                task_id = text_data_json.get("task_id")
                update_results = await database_sync_to_async(update_pass_info)(info_detail_list=info_detail,
                                                                                task_id=task_id,
                                                                                client_user=self.client_user
                                                                                )
                await self.send(text_data=json.dumps(update_results))
            else:
                await self.send(text_data=json.dumps(
                    {
                        'message': 'need_auth'
                    }))
        # 同步人脸数据库
        elif message_type == "sync_database":
            if self.company_id:
                data_sync_type = text_data_json.get('sync_type')

                # 全同步模式
                if data_sync_type == "full_sync":
                    resp_data = await database_sync_to_async(get_face_store)(client_user=self.client_user,
                                                                             data_sync_type=data_sync_type,
                                                                             company_id=self.company_id)
                    await self.send(text_data=json.dumps(resp_data))

                # 检验同步模式,设备发送本地数据库人员列表进行数据量比对
                elif data_sync_type == "check_sync":
                    check_sync_list = text_data_json.get("check_sync_list")
                    resp_data = await database_sync_to_async(get_face_store)(client_user=self.client_user,
                                                                             data_sync_type=data_sync_type,
                                                                             company_id=self.company_id,
                                                                             check_sync_list=check_sync_list)
                    await self.send(text_data=json.dumps(resp_data))

                # 确认比对状态
                elif data_sync_type == "check_finished":
                    check_finished_list = text_data_json.get("check_finished_list")
                    resp_data = await database_sync_to_async(get_face_store)(client_user=self.client_user,
                                                                             data_sync_type=data_sync_type,
                                                                             company_id=self.company_id,
                                                                             check_sync_list=check_finished_list)
                    await self.send(text_data=json.dumps(resp_data))



                # 指定人员同步
                elif data_sync_type == "single_sync":
                    staff_id_list = text_data_json.get('staff_id_list')
                    resp_data = await database_sync_to_async(get_face_store)(data_sync_type=data_sync_type,
                                                                             staff_id_list=staff_id_list)
                    await self.send(text_data=json.dumps(resp_data))


            else:
                await self.send(text_data=json.dumps(
                    {
                        'message': 'need_auth'
                    }))
        # 同步状态
        elif message_type == "sync_info":
            if self.company_id:
                sync_state = text_data_json.get('sync_state')
                state = sync_state.get("state")
                face_data_len = sync_state.get("face_data_len")
                success_sync = sync_state.get("success_sync")
                # 判断同步类型
                if sync_state['type'] == "full_sync":
                    sync_type = "full_sync"
                elif sync_state['type'] == 'single_sync':
                    sync_type = "single"
                elif sync_state['type'] == 'check_sync':
                    sync_type = 'check_sync'
                    face_data_len = 0
                    success_sync = 0
                else:
                    sync_type = ''
                # 进行数据库同步
                await database_sync_to_async(update_sync_state)(sync_type=sync_type,
                                                                sync_state=state,
                                                                client_user=self.client_user,
                                                                face_data_len=face_data_len,
                                                                success_sync=success_sync)

            else:
                await self.send(text_data=json.dumps(
                    {
                        'message': 'need_auth'
                    }))

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
    # 在数据库中检索设备号与认证码
    auth = ClientInfo.objects.filter(client_user=client_user, client_key=client_key)
    # print('auth', auth)
    auth_state = auth.count()
    # print('auth_state', auth_state)
    if auth_state >= 1:
        # 生成设备唯一token
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


def get_face_store(client_user, data_sync_type, company_id=None, staff_id_list=None, check_sync_list=None):
    """
    获取人脸数据库
    """
    if check_sync_list is None:
        check_sync_list = []
    resp_data = {
        'type': data_sync_type,
        'face_store': []
    }
    # 全同步方式
    if data_sync_type == "full_sync":
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
    # 指定人员同步
    elif data_sync_type == "single_sync":
        for single_staff in staff_id_list:
            single_face = FaceStore.objects.filter(staff_id=single_staff).get()
            print('single_face', single_face)
            single_data = {'name': single_face.name,
                           'phone': single_face.phone,
                           'staff_id': single_face.staff_id,
                           'company_id': single_face.company_id,
                           'face_code': str(single_face.face_code)}
            resp_data['face_store'].append(single_data)
        print(len(resp_data['face_store']))
        return resp_data
    # 人员列表检查同步
    elif data_sync_type == "check_sync":
        local_staff_list = []
        for x in FaceStore.objects.filter(company_id=company_id):
            local_staff_list.append(x.staff_id)
        print('local_staff_list', local_staff_list)
        if check_sync_list:
            check_sync_list = check_sync_list
        else:
            check_sync_list = []
        update_list = []
        for check_staff in local_staff_list:
            if check_staff not in check_sync_list:
                update_list.append(check_staff)
        # 检测数据库改动(人脸更新,人脸删除)
        for k in FaceStore.objects.filter(company_id=company_id):
            local_client_list = eval(k.client_sync_list)
            print('local_client_list', local_client_list)
            if client_user in local_client_list:
                pass
            else:
                update_list.append(k.staff_id)
        print('update_list', update_list)
        resp_data['update_list'] = update_list
        return resp_data
    # 确认比对状态
    elif data_sync_type == "check_finished":
        try:
            for single_staff in check_sync_list:
                local_client_list = FaceStore.objects.filter(staff_id=single_staff).get().client_sync_list
                new_local_client_list = eval(local_client_list)
                # print('new_local_client_list', new_local_client_list)
                new_local_client_list.append(client_user)
                # print('new_local_client_list_return', new_local_client_list)
                # 设备号去重
                new_local_client_list = list(set(new_local_client_list))
                FaceStore.objects.filter(staff_id=single_staff).update(client_sync_list=str(new_local_client_list))
        except Exception as e:
            print(e)
        else:
            resp_data['update_state'] = "cool"
            return resp_data


def update_sync_state(sync_type, sync_state, client_user, face_data_len=0, success_sync=0):
    """
    更新同步状态
    """
    try:
        # 全同步
        if sync_type == "full_sync":
            SyncInfo.objects.create(sync_type=sync_type,
                                    sync_state=sync_state,
                                    client_user_id=client_user,
                                    face_data_len=face_data_len,
                                    success_sync=success_sync)
        # 人员列表检查同步
        elif sync_type == "check_sync":
            SyncInfo.objects.create(sync_type=sync_type,
                                    sync_state=sync_state,
                                    client_user_id=client_user)
    except Exception as e:
        print(e)
        return "sync_info_error"
    else:
        return 'ok'


def update_pass_info(info_detail_list, task_id, client_user):
    """
    更新通行日志
    """
    resp_data = {
        'task_id': task_id,
        'pass_update_state': ''
    }
    try:
        # 分条插入数据库中
        for single_info in info_detail_list:
            name = single_info.get('name')
            staff_id = single_info.get('staff_id')
            company_id = single_info.get('company_id')
            pass_time = single_info.get('pass_time')
            PassInfo.objects.create(name=name,
                                    staff_id=staff_id,
                                    company_id=company_id,
                                    pass_time=pass_time,
                                    client_user=client_user)
    except Exception as e:
        print(e)
        resp_data['pass_update_state'] = 'error'
        return resp_data
    else:
        resp_data['pass_update_state'] = 'success'
        return resp_data
