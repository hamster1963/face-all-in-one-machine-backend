# Generated by Django 4.0.3 on 2022-03-10 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('face_machine_client', '0006_alter_passinfo_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passinfo',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
