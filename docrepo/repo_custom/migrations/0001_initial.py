# Generated by Django 3.2.14 on 2022-08-09 00:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('repo', '0002_alter_project_icon'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('document_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='repo.document')),
                ('my_custom_field', models.CharField(blank=True, max_length=255, null=True, verbose_name='My Custom Field')),
            ],
            options={
                'abstract': False,
            },
            bases=('repo.document',),
        ),
    ]