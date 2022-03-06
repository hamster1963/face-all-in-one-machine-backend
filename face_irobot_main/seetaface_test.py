import time

from seeta.faceapi import *

# 引擎初始化
func_list = ["FACE_DETECT", "FACE_RECOGNITION", "LANDMARKER5", "FACE_TRACK"]
model_path = "./seeta/model"
print('model_path', model_path)
seetaFace = SeetaFace(func_list, device=1, id=0)
seetaFace.init_engine(model_path)
print('init_engine', time.time())
image2 = cv2.imread("./images/yoga.jpeg")  # 原图
simage2 = get_seetaImageData_by_numpy(image2)  # 原图转SeetaImageData
# 计算两个特征值的形似度
detect_result2 = seetaFace.Detect(simage2)
face2 = detect_result2.data[0].pos
points2 = seetaFace.mark5(simage2, face2)
feature2 = seetaFace.Extract(simage2, points2)
feature = seetaFace.get_feature_byte(feature2)
print(feature)
print(seetaFace.CalculateSimilarity(feature2, feature2))
print('end', time.time())

