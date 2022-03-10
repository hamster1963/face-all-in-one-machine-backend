import json

from django.http import JsonResponse
from django.shortcuts import render
from admin_manage.models import Company
from admin_manage.views import method_verify
from face_machine_client.models import ClientInfo
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def receive_pass_info():
    """
    接收人脸通行日志
    请求实例
    websocket协议
    {
        "pass_info":[
                {
                    "name": "",
                    "staff_id": "",
                    "company_id": "",
                    "pass_time": ""
                },
                {
                    "name": "",
                    "staff_id": "",
                    "company_id": "",
                    "pass_time": ""
                },
    ]
    }
    """
    pass


@method_verify()
def client_register(request):
    """
    设备注册接口
    请求实例
    {
    'type':'register',
    'username':'',
    'password':'',
    'company_id':'',
    }
    :param request:
    :return:
    {'msg':'ok'}
    """
    req_data = request.POST
    if req_data.get('type') == 'register':
        client_user = req_data.get('client_user')
        client_key = req_data.get('client_key')
        client_company_id = req_data.get('client_company_id')
        if client_user and client_key and client_company_id:
            client_check = ClientInfo.objects.filter(client_user=client_user).count()
            if client_check == 0:
                try:
                    company_id = Company.objects.filter(company_id=client_company_id).get()
                    ClientInfo.objects.create(client_user=client_user, client_key=client_key, client_info=company_id)
                except Exception as e:
                    print(e)
                    return JsonResponse({'msg': str(e)})
                return JsonResponse({'msg': '设备注册成功,请记录设备号与密码',
                                     'username': client_user,
                                     'password': client_key})
            else:
                return JsonResponse({'msg': '设备已经被注册'})
        else:
            return JsonResponse({'msg': '有必填项未填'})

    elif req_data.get('type') == 'delete':
        # 删除设备
        client_user = req_data.get('client_user')
        client_company_id = req_data.get('client_company_id')
        company_id = Company.objects.filter(company_id=client_company_id).get()
        if client_user and client_company_id:
            client_object = ClientInfo.objects.filter(client_user=client_user, client_info=company_id)
            if client_object.count() == 1:
                try:
                    client_object.delete()
                except Exception as e:
                    print(e)
                    return JsonResponse({'msg': str(e)})
                else:
                    return JsonResponse({'msg': '删除成功',
                                         'errorCode': 0})

            elif client_object.count() == 0:
                return JsonResponse({'msg': '设备不存在'})
            else:
                return JsonResponse({'msg': '参数出错'})
        else:
            return JsonResponse({'msg': '有必填项未填'})




    else:
        return JsonResponse({'msg': '注册参数出错'})


@method_verify()
def push_to_client(request):
    """
    主动推送数据至客户端
    """
    req_data = request.POST
    # 推送类型
    push_type = req_data.get('push_type')
    # 按照企业推送全推送
    if push_type == "company":
        company_id = request.POST.get('company_id')
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(  # ASGI是异步的，这里转为同步操作；通过通信层向组群发送消息
                str(company_id),  # 设备的企业id
                {
                    'type': 'get_notification',  # 标记发送事件的type
                    'message': 'you have got a new report',  # 提示信息
                }
            )
        except Exception as e:
            print(e)
            return JsonResponse({'msg': 'push_error'})
        else:
            return JsonResponse({'msg': 'ok'})
    # 单个设备推送
    elif push_type == "single_client":
        client_user = request.POST.get('client_user')
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(  # ASGI是异步的，这里转为同步操作；通过通信层向组群发送消息
                str(client_user),  # 设备的设备号
                {
                    'type': 'get_notification',  # 标记发送事件的type
                    'message': 'you have got a new report',  # 提示信息
                }
            )
        except Exception as e:
            print(e)
            return JsonResponse({'msg': 'push_error'})
        else:
            return JsonResponse({'msg': 'ok'})

