from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    # ロールの種類を指定
    ROLE_CHOICES = [
        ('player', '選手'),
        ('manager', 'マネージャー'),
        ('coach', 'コーチ'),
        ('director', '監督'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='player')  # roleを指定した種類の選択式にしてモデルに追加
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日時をモデルに追加 - 作成時に自動セット
    updated_at = models.DateTimeField(auto_now=True)      # 更新日時をモデルに追加 - 更新時に自動更新

    def __str__(self):
        return f"{self.username} ({self.role})"
