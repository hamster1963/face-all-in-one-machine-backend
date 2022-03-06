from django.urls import path
from admin_manage import views

urlpatterns = [
    path('verify', views.login, name='登录'),
    path('register', views.register, name='注册'),
    path('token_test', views.token_test, name='token测试'),
    path('code', views.create_img_code, name='验证码生成'),
    path('img_test', views.image_test, name='图片测试'),
]
