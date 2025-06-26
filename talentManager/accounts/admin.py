from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm

# Register your models here.
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2'),
        }),
    ) # UserAdmin.add_fieldsets に追加ではなく明示的に追加

    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')

admin.site.register(CustomUser, CustomUserAdmin)
