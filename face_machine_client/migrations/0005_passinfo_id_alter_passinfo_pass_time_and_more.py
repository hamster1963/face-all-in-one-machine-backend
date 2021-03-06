# Generated by Django 4.0.3 on 2022-03-10 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('face_machine_client', '0004_syncinfo_face_data_len_syncinfo_success_sync'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passinfo',
            name='staff_id',
            field=models.IntegerField(verbose_name='员工id'),
        ),
        migrations.AddField(
            model_name='passinfo',
            name='id',
            field=models.IntegerField(auto_created=True, default=1, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='passinfo',
            name='pass_time',
            field=models.DateTimeField(auto_now=True, verbose_name='通行时间'),
        ),

    ]
