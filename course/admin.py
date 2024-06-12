from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Group, CourseAllocation, Upload


admin.site.register(Group)
admin.site.register(CourseAllocation)
admin.site.register(Upload)
