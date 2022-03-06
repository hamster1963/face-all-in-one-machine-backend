import json

from django.shortcuts import render

from admin_manage.views import method_verify
from face_machine_client.models import ClientInfo

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


def index(request):
    return render(request, 'chat/index.html', {})


from django.utils.safestring import mark_safe


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })


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
    '''req_data = request.POST
    if req_data.get('type') == 'register':
        client_user = req_data.get('client_user')
        client_key = req_data.get('client_key')
        client_company_id = req_data.get('company_id')
        if client_user and client_key and client_company_id:
            client_check = ClientInfo.objects.filter(client_user=client_user).count()
            if client_check == 0:
                try:
                    company = 1
                    ClientInfo.objects.create(client_user=client_user, client_key=client_key,)
                except Exception as e:
                    print(e)
                    return JsonResponse({'msg': str(e)})
                return JsonResponse({'msg': '注册成功,请记录用户名与密码',
                                     'username': username,
                                     'password': password})
            else:
                return JsonResponse({'msg': '用户名已经被注册'})
        else:
            return JsonResponse({'msg': '有必填项未填'})
    else:
        return JsonResponse({'msg': '注册参数出错'})'''
