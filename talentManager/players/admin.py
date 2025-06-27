from django.contrib import admin

# Register your models here.
from .models import StudentProfile
from players.models import PlayerProfile

class PlayerProfileInline(admin.StackedInline):
    model = PlayerProfile
    can_delete = False
    verbose_name_plural = 'プレイヤープロフィール'

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    inlines = [PlayerProfileInline]
    list_display = ('user', 'grade', 'class_number', 'joined_at', 'status')
    list_filter = ('grade', 'status')
