# Generated by Django 4.2.10 on 2024-03-02 17:05

import apps.shared.mixins
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.PositiveIntegerField()),
                ('y', models.PositiveIntegerField()),
                ('description', models.CharField(max_length=128)),
                ('status', models.IntegerField(choices=[(1, 'active'), (2, 'done'), (3, 'failed')], default=1)),
            ],
            options={
                'abstract': False,
            },
            bases=(apps.shared.mixins.Visualizable, models.Model),
        ),
        migrations.CreateModel(
            name='TaskSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remove_task_on', models.IntegerField(choices=[(1, 'active'), (2, 'done'), (3, 'failed')])),
            ],
            bases=(apps.shared.mixins.Visualizable, models.Model),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('global_task_settings', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='tasks.tasksettings')),
                ('tasks', models.ManyToManyField(blank=True, to='tasks.task')),
            ],
            bases=(apps.shared.mixins.Visualizable, models.Model),
        ),
        migrations.AddField(
            model_name='task',
            name='settings',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tasks.tasksettings'),
        ),
    ]