from django import forms
from accounts.models import CustomUser
from players.models import StudentProfile, PlayerProfile
from .models import MeasurementRecord, MeasurementItem
from django.forms import inlineformset_factory

class MemberCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="パスワード")
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, label="ユーザー種別")
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'role')

class StudentProfileForm(forms.ModelForm):
    grade = forms.IntegerField(label="学年")
    class_number = forms.CharField(label="クラス")
    joined_at = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        ),
        label="入部日"
    )
    status = forms.ChoiceField(
        choices=StudentProfile.STATUS_CHOICES,
        label="ステータス"
    )
    leave_reason = forms.CharField(
        required=False,
        label="退部理由",
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 40})
    )
    class Meta:
        model = StudentProfile
        fields = ['grade', 'class_number', 'joined_at', 'status', 'leave_reason']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # フィールドをすべて optional に（手動で制御）
        for field in self.fields.values():
            field.required = False

class PlayerProfileForm(forms.ModelForm):
    position = forms.CharField(label="ポジション")
    jersey_number = forms.IntegerField(label="背番号")
    class Meta:
        model = PlayerProfile
        fields = ('position', 'jersey_number')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # フィールドをすべて optional に（手動で制御）
        for field in self.fields.values():
            field.required = False

class MeasurementForm(forms.ModelForm):
    class Meta:
        model = MeasurementRecord
        fields = ['player', 'measured_at']

MeasurementItemFormSet = inlineformset_factory(
    MeasurementRecord,
    MeasurementItem,
    fields=('category', 'item_name', 'value', 'unit'),
    extra=4,
    can_delete=False
)

