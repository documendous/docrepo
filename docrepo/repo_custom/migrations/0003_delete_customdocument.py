# Generated by Django 3.2.14 on 2022-08-11 15:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0004_alter_favoritedocument_document'),
        ('repo_custom', '0002_auto_20220809_0059'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomDocument',
        ),
    ]
