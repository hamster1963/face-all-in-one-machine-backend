import datetime
import time

import cv2
import numpy as np
from django.http import JsonResponse
from django.shortcuts import render
from face_irobot_main.img_utils import full_aspect_face_detect, get_feature, calculate, face_data_main, compare_in_list
from functools import wraps
from admin_manage.views import verify_token
from face_irobot_main.models import FaceStore


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
                return JsonResponse({'msg': '请求方法错误'})

        return wrapper

    return method_check


# @verify_token
@method_verify()
def face_main(request):
    """
    人脸审核接口主函数
    请求样式:
    {
    "phone":"17707500769",
    "name":"廖",
    "staff_id":"72791",
    "company_id":"163",
    "Type":"registerPersonPhoto",
    "photo":"file"
    }
    返还json:  resp_data = {'msg': 'ok'}
    """
    req_data = request.POST
    if req_data.get('Type') != "registerPersonPhoto":
        return JsonResponse({'msg': '请求参数错误'})
    # 检测请求参数
    req_data_json = {"phone": req_data.get('phone'),
                     "name": req_data.get('name'),
                     "staff_id": req_data.get('staff_id'),
                     "company_id": req_data.get('company_id'),
                     "Type": req_data.get('Type'),
                     }
    for x in req_data_json:
        if not req_data_json[x]:
            return JsonResponse({'msg': '有必填项' + x + '为空'})
    try:
        if 'photo' in request.FILES:
            # 判断请求参数是否符合要求
            file = request.FILES.get('photo')
            img_type = file.name.split('.')[-1]
            if img_type not in ['jpeg', 'jpg', 'png']:
                resp_data = {'msg': 'wrong_img_type',
                             }
                return JsonResponse(resp_data)
            img = file.read()
            # 是用opencv解码
            img_file = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
            # 调用主函数
            face_detect = full_aspect_face_detect(img_file=img_file)
            face_result = face_detect[0]
            # 如果未检测到人脸返还错误信息
            if face_result != "face_detect_ok":
                # json返还检测结果
                resp_data = {'msg': face_result,
                             }
                return JsonResponse(resp_data)
            # 检测到人脸进行图像处理
            elif face_result == "face_detect_ok":
                # 进入人脸图像处理
                try:
                    # 图像处理
                    print('开始图像处理')
                    print('进行人脸特征值提取')

                    try:
                        face_code = get_feature(face_detect[1])
                    except Exception as e:
                        print(e)
                        return JsonResponse({'msg': '提取特征值过程出错'})

                    try:
                        face_store_check = FaceStore.objects.filter(phone=req_data.get('phone')).count()
                        if face_store_check != 0:
                            Update_face = FaceStore.objects.filter(phone=req_data.get('phone')).get()
                            Update_face.face_code = face_code
                            Update_face.upload_time = datetime.datetime.now()
                            Update_face.save()
                            return JsonResponse({'msg': '人脸照片更新成功'})
                        else:
                            FaceStore.objects.create(staff_id=int(req_data.get('staff_id')),
                                                     company_id=int(req_data.get('company_id')),
                                                     name=req_data.get('name'),
                                                     phone=req_data.get('phone'),
                                                     face_code=face_code,
                                                     upload_time=datetime.datetime.now()
                                                     )
                            return JsonResponse({'msg': '人脸照片上传成功'})
                    except Exception as e:
                        print(e)
                        return JsonResponse({'msg': '存储特征值过程出错'})

                except Exception as e:
                    print(e)
        else:
            # 非法格式
            resp_data = {'msg': '未获取到图像'
                         }
            return JsonResponse(resp_data)
    except Exception as e:
        print(e)
        resp_data = {'msg': 'wrong'}
        return JsonResponse(resp_data)


@method_verify()
def delete_face_main(request):
    """
    删除人脸信息
    请求样式:
    {
	"token": "dGltZT0xNjQ1MjgwMzU5bnVtPTk0OTk=",
	"Type": "deletePersonPhoto",
	"phone": "110",
	"name": "林宥嘉",
	"staff_id": "77777",
	"company_id": "999",
    }
    """
    req_data = request.POST
    if req_data.get('Type') == "deletePersonPhoto":
        req_data_json = {"phone": req_data.get('phone'),
                         "name": req_data.get('name'),
                         "staff_id": req_data.get('staff_id'),
                         "company_id": req_data.get('company_id'),
                         }
        for x in req_data_json:
            if not req_data_json[x]:
                return JsonResponse({'msg': '有必填项' + x + '为空'})
        try:
            delete_object = FaceStore.objects.filter(phone=req_data_json['phone'],
                                                     name=req_data_json['name'],
                                                     staff_id=req_data_json['staff_id'],
                                                     company_id=req_data_json['company_id']).get()
            delete_object.face_code = ''.encode()
            delete_object.save()
        except Exception as e:
            print(e)
            return JsonResponse({'msg': '删除出错'})
        else:
            return JsonResponse({'msg': '用户' + req_data_json['name'] + '人脸信息删除完成'})

    else:
        return JsonResponse({'msg': '请求参数不正确'})


# @verify_token
@method_verify()
def compare_face(request):
    """
    比对两张人脸照片
    请求样式:
    {
    "Type":"compareFace",
    "photo1":"file",
    "photo2":"file"
    }
    返还json:  resp_data = {'msg': 'ok'}
    """
    if 'photo1' and 'photo2' in request.FILES:
        # 判断请求参数是否符合要求
        file1 = request.FILES.get('photo1')
        file2 = request.FILES.get('photo2')
        img_type1 = file1.name.split('.')[-1]
        img_type2 = file2.name.split('.')[-1]
        if img_type1 not in ['jpeg', 'jpg', 'png'] or img_type2 not in ['jpeg', 'jpg', 'png']:
            resp_data = {'msg': 'wrong_img_type',
                         }
            return JsonResponse(resp_data)
        img1 = file1.read()
        img2 = file2.read()
        # 是用opencv解码
        img_file1 = cv2.imdecode(np.frombuffer(img1, np.uint8), cv2.IMREAD_COLOR)
        img_file2 = cv2.imdecode(np.frombuffer(img2, np.uint8), cv2.IMREAD_COLOR)
        img1_code = get_feature(img_file1)
        img2_code = get_feature(img_file2)
        if img1_code and img2_code:
            sim = calculate(img1_code, img2_code)
            return JsonResponse({'msg': '两张人脸相似度为' + str(sim)})
        elif not img1_code:
            return JsonResponse({'msg': '未获取到图片1的人脸信息'})
        elif not img2_code:
            return JsonResponse({'msg': '未获取到图片2的人脸信息'})
    else:
        return JsonResponse({'msg': '未获取到两张图像'})


# @verify_token
@method_verify()
def find_face(request):
    """
    从数据库中寻找图片中的人名
    """
    name_list = face_data_main()[0]
    face_code_list = face_data_main()[1]
    # print('name_list', name_list)
    # print('face_code_list', face_code_list)
    if 'photo' in request.FILES:
        file = request.FILES.get('photo')
        img_type = file.name.split('.')[-1]
        if img_type not in ['jpeg', 'jpg', 'png']:
            resp_data = {'msg': 'wrong_img_type',
                         }
            return JsonResponse(resp_data)
        img = file.read()
        # 是用opencv解码
        img_file = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
        img_code = get_feature(img_file)
        result = compare_in_list(img_code, name_list, face_code_list)
        if result != 'NOT_FOUND':
            return JsonResponse({'msg': '在数据库中找到该人员',
                                 'name': result[0],
                                 'similarity': result[1]})
        else:
            return JsonResponse({'msg': '未在数据库中找到'})
    else:
        return JsonResponse({'msg': '未获取到图像'})
