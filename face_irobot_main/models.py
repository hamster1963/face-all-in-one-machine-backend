from django.db import models


# Create your models here.
class FaceStore(models.Model):
    face_url = models.CharField(default='', max_length=50, verbose_name='人脸照片地址')
    staff_id = models.IntegerField(primary_key=True, verbose_name='员工id')
    company_id = models.IntegerField(default=999, verbose_name='企业id')
    name = models.CharField(max_length=50, verbose_name='姓名')
    phone = models.CharField(max_length=20, verbose_name='手机号码')
    face_code = models.BinaryField(verbose_name='人脸特征码')
    upload_time = models.DateTimeField(verbose_name='人脸上传日期')
    sync_state = models.IntegerField(default=0, verbose_name='与设备同步状态')

