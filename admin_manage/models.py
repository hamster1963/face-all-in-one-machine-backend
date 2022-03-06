from django.db import models

# Create your models here.
from django.db import models


class Company(models.Model):
    company_id = models.IntegerField(default=9999, verbose_name='企业id', primary_key=True)


# Create your models here.
class Admin(models.Model):
    username = models.CharField(max_length=30, verbose_name='管理员用户名')
    password = models.CharField(max_length=30, verbose_name='密码')
    open_state = models.IntegerField(default=1, verbose_name='启用状态')
    admin_info = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='company_admin')


class Token(models.Model):
    token = models.CharField(max_length=50, verbose_name='token')
    username = models.CharField(max_length=30, verbose_name='用户名')
    admin_info = models.ForeignKey('Admin', on_delete=models.CASCADE, related_name='admin_token')
