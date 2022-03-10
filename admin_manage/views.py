from django.shortcuts import render

# Create your views here.
import time
import random
import base64
from io import BytesIO
from functools import wraps
from django.http import JsonResponse, HttpResponse
from admin_manage.models import Admin, Token, Company
from PIL import Image


def method_verify(req_method='POST'):
    """
    请求方法检测
    :param req_method:
    :return:
    """

    def method_check(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            method = request.method
            if method == req_method:
                return func(request, *args, **kwargs)
            else:
                return JsonResponse({'msg': '请求方法错误',
                                     'code': "200",
                                     'error': "001",
                                     })

        return wrapper

    return method_check


def verify_token(func):
    """
    token验证
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            token = request.POST['token']
        except Exception as e:
            print('token_error', str(e))
            return JsonResponse({'msg': '未获取到token',
                                 'code': "200",
                                 'error_code': "999"
                                 })
        else:
            try:
                # 在数据库中查询token
                token_check = Token.objects.filter(token=token)
                token_num = token_check.count()
            except Exception as e:
                return JsonResponse({'msg': str(e)})
            # 如果未查询到token，返还
            if token_num == 0:
                return JsonResponse({'msg': 'token错误',
                                     'code': "200",
                                     'error_code': "998"
                                     }, json_dumps_params={'ensure_ascii': False})
            # 查询到token，判断是否过期
            else:
                re_token = base64.b64decode(token).decode('utf-8').split('num=')
                time_check = re_token[0].split('time=')[1]
                time_check = (int(time.time()) - int(time_check)) / 60
                if time_check > 30:  # 如果token过期，返还
                    return JsonResponse({'msg': 'token过期',
                                         'code': "200",
                                         'error_code': "997"
                                         })
                else:
                    return func(request, *args, **kwargs)

    return wrapper


@method_verify(req_method='GET')
# 生成验证码
def create_img_code(request):
    """
    生成验证码
    :return:
    """
    from PIL import Image, ImageDraw
    import random
    # 图片大小的宽度和高度
    size = (100, 30)
    # 创建图片
    image = Image.new('RGB', size, (255, 255, 255))
    # 创建画笔
    draw = ImageDraw.Draw(image)
    # 生成随机验证码
    code_list = []
    for i in range(5):
        current_num = str(random.randint(0, 9))
        current_char = random.choice([current_num])
        code_list.append(current_char)
        draw.text((i * 20, 10), current_char, fill=(0, 0, 0,), )
    # 将生成的验证码保存到session中
    code = ''.join(code_list)
    request.session['code'] = code
    # 将验证码图片保存到内存中，防止用户禁用cookie
    buf = BytesIO()
    image.save(buf, 'png')
    data = buf.getvalue()
    buf.close()
    return HttpResponse(data, 'image/png')


def create_token(username, admin_info):
    """
    生成token
    :return:token
    """
    # --1.生成token--
    token = 'time=' + str(int(time.time())) + 'num=' + str(random.randint(1000, 9999))
    token = base64.b64encode(token.encode('utf-8')).decode('utf-8')
    print('token', token)
    # --2.存入数据库--
    try:
        token_save = Token.objects.create(token=token, username=username, admin_info=admin_info)
        token_save.save()
    except Exception as e:
        print(e)
        return 'token_create_wrong'
    else:  # 成功后返还token
        return token


@method_verify()
def login(request):
    """
    登录接口
    请求示例
    {'username':'',
    'password':''
    }
    :param request:
    :return:
    """
    req_data = request.POST
    username = req_data.get('username')
    password = req_data.get('password')
    if not username or not password:
        return JsonResponse({'msg': '用户名或密码不能为空',
                             'code': "200",
                             'error_code': "888"
                             }, json_dumps_params={'ensure_ascii': False})
    code = req_data.get('code')  # 获取验证码

    if code and request.session.get('code') and int(code) == int(request.session.get('code')):  # 验证二维码
        pass
    else:
        return JsonResponse({'msg': '验证码错误',
                             'code': "200",
                             'error_code': "887"
                             }, json_dumps_params={'ensure_ascii': False})
    try:  # 登录
        login_check = Admin.objects.filter(username=username, password=password)
        login_state = login_check.count()
    except Exception as e:
        return JsonResponse({'msg': str(e)}, json_dumps_params={'ensure_ascii': False})
    if login_state == 0:
        return JsonResponse({'msg': '用户名或密码不存在',
                             'code': "200",
                             'error_code': "886"
                             }, json_dumps_params={'ensure_ascii': False})
    else:  # 检验账户状态
        user_state = login_check.get().open_state
        if user_state == 1:
            token = create_token(username, login_check.get())
            request.session['code'] = 0
            return JsonResponse({'msg': '登录成功',
                                 'token': token,
                                 'company_id': login_check.get().admin_info.company_id,
                                 'code': "200",
                                 'error_code': "0"
                                 })
        else:
            return JsonResponse({'msg': '账号被停用',
                                 'code': "200",
                                 'error_code': "880"
                                 }, json_dumps_params={'ensure_ascii': False})


@method_verify()
def register(request):
    """
    注册接口
    请求实例
    {
    'Type':'register',
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
        username = req_data.get('username')
        password = req_data.get('password')
        company_id = req_data.get('company_id')
        # 检查必填项是否已填
        if username and password and company_id:
            request_check = Admin.objects.filter(username=username).count()
            # 检查用户名是否已经注册
            if request_check == 0:
                try:
                    admin_info = Company.objects.filter(company_id=company_id).get()
                    Admin.objects.create(username=username, password=password, admin_info=admin_info)
                except Exception as e:
                    print(e)
                    return JsonResponse({'msg': str(e)})
                return JsonResponse({'msg': '注册成功,请记录用户名与密码',
                                     'username': username,
                                     'password': password,
                                     'code': "200",
                                     'error_code': "0"
                                     })
            else:
                return JsonResponse({'msg': '用户名已经被注册',
                                     'code': "200",
                                     'error_code': "885"
                                     })
        else:
            return JsonResponse({'msg': '有必填项未填',
                                 'code': "200",
                                 'error_code': "884"
                                 })
    else:
        return JsonResponse({'msg': '注册参数出错',
                             'code': "200",
                             'error_code': "883"
                             })


@method_verify()
@verify_token
def token_test(request):
    """
    token验证测试接口
    :param request:
    :return:
    """
    return JsonResponse({'msg': 'token验证成功'}, json_dumps_params={'ensure_ascii': False})


def image_test(request):
    file = request.FILES.get('photo')
    img = Image.open(file)
    img.save('./123.jpg')
    return JsonResponse({'msg': 'ok'})
