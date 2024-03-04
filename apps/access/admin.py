from django.contrib import admin

from apps.access import models


admin.site.register(models.User)
