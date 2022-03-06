# Generated by Django 4.0.3 on 2022-03-06 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FaceStore',
            fields=[
                ('face_url', models.CharField(default='', max_length=50, verbose_name='人脸照片地址')),
                ('staff_id', models.IntegerField(primary_key=True, serialize=False, verbose_name='员工id')),
                ('company_id', models.IntegerField(default=999, verbose_name='企业id')),
                ('name', models.CharField(max_length=50, verbose_name='姓名')),
                ('phone', models.CharField(max_length=20, verbose_name='手机号码')),
                ('face_code', models.BinaryField(verbose_name='人脸特征码')),
                ('upload_time', models.DateTimeField(verbose_name='人脸上传日期')),
            ],
        ),
    ]