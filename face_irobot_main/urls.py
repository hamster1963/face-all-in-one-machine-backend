from django.urls import path

from . import views

urlpatterns = [
    path('upload_face', views.face_main, name='人脸测试'),
    path('compare_face', views.compare_face, name='人脸比对'),
    path('find_face', views.find_face, name='人脸与数据库比对获取姓名'),
    path('delete', views.delete_face_main, name='删除人脸信息')
]