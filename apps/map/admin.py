from django.contrib import admin

from apps.map import models


admin.site.register(models.User)
admin.site.register(models.Task)
admin.site.register(models.TaskSettings)
