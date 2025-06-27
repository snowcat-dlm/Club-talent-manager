from django import forms
from accounts.models import CustomUser
from players.models import StudentProfile, PlayerProfile

class MemberCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)

    # StudentProfile
    grade = forms.IntegerField()
    class_number = forms.CharField(required=False)
    joined_at = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'role', 'grade', 'class_number', 'joined_at')

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['grade', 'class_number', 'joined_at', 'status', 'leave_reason']

class PlayerProfileForm(forms.ModelForm):
    class Meta:
        model = PlayerProfile
        fields = ('position', 'jersey_number')
