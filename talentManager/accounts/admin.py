from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm
from players.models import StudentProfile, PlayerProfile

# --- StudentProfile をインラインで表示する設定 ---
class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = '学生プロフィール'

# --- カスタムユーザー管理画面の定義 ---
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    model = CustomUser
    inlines = [StudentProfileInline]

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

# --- 管理画面に登録 ---
admin.site.register(CustomUser, CustomUserAdmin)
