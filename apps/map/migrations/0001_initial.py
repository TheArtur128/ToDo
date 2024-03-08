# Generated by Django 4.2.10 on 2024-03-08 13:13

import apps.shared.mixins
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.PositiveIntegerField()),
                ('y', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
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
                ('global_task_settings', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='map.tasksettings')),
            ],
            bases=(apps.shared.mixins.Visualizable, models.Model),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.PositiveIntegerField()),
                ('y', models.PositiveIntegerField()),
                ('description', models.CharField(max_length=128)),
                ('status', models.IntegerField(choices=[(1, 'active'), (2, 'done'), (3, 'failed')], default=1)),
                ('root_map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='map.map')),
                ('settings', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='map.tasksettings')),
                ('submap', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='map.map')),
            ],
            options={
                'abstract': False,
            },
            bases=(apps.shared.mixins.Visualizable, models.Model),
        ),
        migrations.CreateModel(
            name='MapTop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('next', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='previous', to='map.maptop')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='maps', to='map.user')),
            ],
        ),
        migrations.AddField(
            model_name='map',
            name='global_task_settings',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='map.tasksettings'),
        ),
        migrations.AddField(
            model_name='map',
            name='top',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='map', to='map.maptop'),
        ),
    ]
