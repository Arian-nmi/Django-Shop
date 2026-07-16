from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from accounts.models import User, Profile


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('id', 'email', 'is_staff', 'is_active', 'is_verified')
    list_filter = ('email', 'is_staff', 'is_active', 'is_verified')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active', 'type')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)


class CustomProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = ('id', 'user', 'first_name', 'last_name', 'phone_number')
    search_fields = ('user', 'first_name', 'last_name', 'phone_number')
    fieldsets = (
        (None, {'fields': ('user', 'first_name', 'last_name', 'phone_number', 'image')}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, CustomProfileAdmin)