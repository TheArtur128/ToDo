from django.contrib import admin

from shared.models import User, Task, Zone, TaskSettings


admin.site.register(User)
admin.site.register(Task)
admin.site.register(Zone)
admin.site.register(TaskSettings)
