from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import PhoneOTP, Requestor, Gigster, Skills, GigsterSkills, Project, GigsterProject

User = get_user_model() 

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form     = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display  = ('first_name', 'phone_number', 'email', 'user_type', 'admin', 'is_active','created_at',)
    list_filter   = ('admin', 'active', 'staff',)
    fieldsets     = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': (['first_name','last_name', 'email','user_type', 'gender'])}),
        ('Permissions', {'fields': ('admin', 'staff', 'active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2')}
        ),
    )
    # readonly_fields = ('created_at', 'updated_at',)
    search_fields = ('phone_number','email', 'first_name', 'last_name', 'user_type','created_at')
    ordering = ('created_at',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.register(PhoneOTP)
admin.site.register(Requestor)
admin.site.register(Gigster)
admin.site.register(Skills)
admin.site.register(GigsterSkills)
admin.site.register(Project)
admin.site.register(GigsterProject)



# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)

