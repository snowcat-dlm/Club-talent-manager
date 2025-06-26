from django.db import models
from accounts.models import CustomUser  # カスタムユーザーを参照するため

# Create your models here.

# 学生プロフィールモデル（マネージャー・選手共通）
class StudentProfile(models.Model):
    STATUS_CHOICES = [
        ('active', '在籍'),
        ('retired', '退部'),
        ('graduated', '卒業'),
        ('suspended', '休部'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  # ユーザーに対する1対1の関連
    grade = models.IntegerField()  # 学年（例：1〜3）
    class_number = models.CharField(max_length=10, blank=True, null=True)  # クラス（例：1-A）
    joined_at = models.DateField()  # 入部日
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')  # 状態（退部など）
    left_at = models.DateField(blank=True, null=True)  # 退部・卒業日
    leave_reason = models.TextField(blank=True, null=True)  # 退部理由など

    def __str__(self):
        return f'{self.user.username} ({self.grade}年)'

# 選手プロフィールモデル（StudentProfileを拡張）
class PlayerProfile(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)  # 学生プロフィールと1対1
    position = models.CharField(max_length=50, blank=True, null=True)  # 守備位置
    jersey_number = models.IntegerField(blank=True, null=True)  # 背番号

    def __str__(self):
        return f'{self.student.user.username} 背番号:{self.jersey_number}'

# 測定記録モデル
class MeasurementRecord(models.Model):
    STATUS_CHOICES = [
        ('draft', '下書き'),
        ('awaiting_player_approval', '選手確認待ち'),
        ('awaiting_coach_approval', 'コーチ確認待ち'),
        ('approved', '確定'),
    ]

    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)  # 測定対象の選手
    measured_at = models.DateField()  # 測定日
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')  # ステータス
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_records')  # 作成者（マネージャー想定）
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日時
    updated_at = models.DateTimeField(auto_now=True)  # 更新日時

    def __str__(self):
        return f'{self.player.student.user.username} 測定日: {self.measured_at}'

# 測定項目モデル
class MeasurementItem(models.Model):
    CATEGORY_CHOICES = [
        ('走力', '走力'),
        ('肩力', '肩力'),
        ('打力', '打力'),
        ('筋力', '筋力'),
    ]

    record = models.ForeignKey(MeasurementRecord, on_delete=models.CASCADE, related_name='items')  # 測定記録への関連
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)  # 測定カテゴリ（例：走力）
    item_name = models.CharField(max_length=50)  # 測定項目名（例：50m走）
    value = models.FloatField()  # 計測値（数値）
    unit = models.CharField(max_length=10, blank=True, null=True)  # 単位（例：秒, km/h）

    def __str__(self):
        return f'{self.item_name}: {self.value}{self.unit or ""}'

# 承認ステータスモデル（選手とコーチによる承認）
class ApprovalStatus(models.Model):
    ROLE_CHOICES = [
        ('player', '選手'),
        ('coach', 'コーチ'),
    ]
    STATUS_CHOICES = [
        ('pending', '保留'),
        ('approved', '承認'),
        ('rejected', '否認'),
    ]

    record = models.ForeignKey(MeasurementRecord, on_delete=models.CASCADE)  # 対象の測定記録
    approver = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # 承認者（ユーザー）
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)  # 承認者の役割
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # 承認ステータス
    approved_at = models.DateTimeField(blank=True, null=True)  # 承認日時
    comment = models.TextField(blank=True, null=True)  # コメント（否認理由など）

    def __str__(self):
        return f'{self.approver.username} ({self.role}) - {self.status}'
