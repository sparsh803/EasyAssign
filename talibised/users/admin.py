from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Project, Submission, Comment


class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff',
        'userType'
    )

    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'userType')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Additional info', {
            'fields': ()
        })
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2', 'userType')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Additional info', {
            'fields': ()
        })
    )





admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Project)
admin.site.register(Submission)
admin.site.register(Comment)
