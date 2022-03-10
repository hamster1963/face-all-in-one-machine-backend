import time
import dlib
import face_irobot_main.facial_feature_detector as feature_detection
from FACE_BACKEND.settings import BASE_DIR
from face_irobot_main.seeta.faceapi import *
from face_irobot_main.models import FaceStore

"""
人脸功能模块文件
"""


# 引擎初始化
func_list = ["FACE_DETECT", "FACE_RECOGNITION", "LANDMARKER5", "FACE_TRACK"]
model_path = "./face_irobot_main/seeta/model"
print('model_path', model_path)
seetaFace = SeetaFace(func_list, device=1, id=0)
seetaFace.init_engine(model_path)
print('init_engine', time.time())

# 正向人脸识别模型路径
predictor_path = str(BASE_DIR) + "/face_irobot_main/dlib_models/shape_predictor_68_face_landmarks.dat"
# 构造检测器
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)


def detect_front_face(img):
    """
    检测正面人脸
    :param img:
    :return:
    """
    lmarks = feature_detection.get_landmarks(img, detector, predictor)
    if len(lmarks):
        return 'OK'
    else:
        return 'NO'


def full_aspect_face_detect(img_file):
    """
    全脸检测
    :param img_file:
    :return:
    """
    state = ''
    trans_img = cv2.transpose(img_file)
    origin_result = detect_front_face(img_file)
    if origin_result == 'OK':
        print('原图检测到人脸')
        # cv2.imwrite('test.png', img_file)
        state = 'face_detect_ok'
        return state, img_file
    else:
        print('开始旋转图片')
        for x in [1, 0]:  # 顺时针或逆时针旋转90度
            new_img = cv2.flip(trans_img, x)
            result = detect_front_face(new_img)  # 再次检测图像
            if result == 'OK' and x == 1:
                print('顺时针转90度')
                # cv2.imwrite('1-90.png', new_img)
                state = 'face_detect_ok'
                return state, new_img
            elif result == 'OK' and x == 0:
                print('逆时针转90度')
                # cv2.imwrite('1+90.png', new_img)
                state = 'face_detect_ok'
                return state, new_img
        if state == '':
            state = 'face_detect_false'
            return state, None


def get_feature(img_file):
    """
    进行人脸特征值提取
    :param img_file:
    :return:feature
    """
    # 原图转SeetaImageData
    simage2 = get_seetaImageData_by_numpy(img_file)
    # 对图像进行检测
    detect_result2 = seetaFace.Detect(simage2)
    # 如果检测到人脸
    if detect_result2.size != 0:
        face = detect_result2.data[0].pos
        points = seetaFace.mark5(simage2, face)
        # 进行特征值提取
        feature = seetaFace.Extract(simage2, points)
    else:
        return None

    return feature


def calculate(feature1, feature2):
    """
    计算特征值相似度
    :param feature1:特征值1
    :param feature2:特征值2
    :return:distance:距离
    """
    distance = seetaFace.CalculateSimilarity(feature1, feature2)
    return distance


def face_data_main():
    """
    获取人脸名字特征值列表
    return some list:返还姓名与c_float特征值list
    """
    # 从数据库提取人名与特征码
    name_list = []
    face_list = []
    face_code_list = []
    face_objects = FaceStore.objects.all()
    for x in face_objects:
        name_list.append(x.name)
        face_list.append(x.face_code)
    for face in face_list:
        single_face_code = seetaFace.get_feature_by_byte(face)
        face_code_list.append(single_face_code)
    return name_list, face_code_list


def compare_in_list(face_code, name_list, face_code_list):
    """
    在列表格式[]中比对
    """
    pre_list = []
    for feature in face_code_list:
        similar = seetaFace.CalculateSimilarity(face_code, feature)
        print('similar', similar)
        if similar >= 0.6:
            pre_list.append((name_list[face_code_list.index(feature)], similar))
        pre_list.sort(key=lambda x: x[1], reverse=True)
        print('pre_list', pre_list)
    if pre_list:
        print(pre_list[0][0])
        return pre_list[0][0], pre_list[0][1]
    else:
        return 'NOT_FOUND'

