from mainapp.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class MyUserInline(admin.StackedInline):
    model = MyUser
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines = (MyUserInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Department)
admin.site.register(Literature)
admin.site.register(Favorites)