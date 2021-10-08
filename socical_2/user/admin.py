from django.contrib import admin

from .models import user_profile


# Register your models here.

admin.site.site_header = 'Quản Lý Cài Đặt Web'

admin.site.register(user_profile)






