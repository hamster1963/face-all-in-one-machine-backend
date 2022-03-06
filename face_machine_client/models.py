from django.db import models


class PassInfo(models.Model):
    """
    日志模块
    """
    name = models.CharField(max_length=10, verbose_name="姓名")
    staff_id = models.IntegerField(primary_key=True, verbose_name='员工id')
    company_id = models.IntegerField(default=999, verbose_name='企业id')
    pass_time = models.DateTimeField(verbose_name='通行时间')


class ClientInfo(models.Model):
    """
    设备模块
    """
    client_user = models.CharField(max_length=15, verbose_name='设备唯一号', unique=True, primary_key=True)
    client_key = models.CharField(max_length=20, verbose_name='设备认证密码')
    client_token = models.CharField(max_length=50, verbose_name='设备token', default='')
    client_info = models.ForeignKey('admin_manage.Admin', on_delete=models.CASCADE, related_name='client_info',
                                    verbose_name='设备企业信息')
    # client_version
    # client_create_time
