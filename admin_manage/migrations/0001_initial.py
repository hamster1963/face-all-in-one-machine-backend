# Generated by Django 4.0.3 on 2022-03-06 23:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30, verbose_name='管理员用户名')),
                ('password', models.CharField(max_length=30, verbose_name='密码')),
                ('open_state', models.IntegerField(default=1, verbose_name='启用状态')),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('company_id', models.IntegerField(default=9999, primary_key=True, serialize=False, verbose_name='企业id')),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=50, verbose_name='token')),
                ('username', models.CharField(max_length=30, verbose_name='用户名')),
                ('admin_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admin_token', to='admin_manage.admin')),
            ],
        ),
        migrations.AddField(
            model_name='admin',
            name='admin_info',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_admin', to='admin_manage.company'),
        ),
    ]
