from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import CustomUser
from accounts.forms import CustomUserCreationForm
from .decorators import coach_or_director_required
from django.conf import settings  #settings.pyをインポート


# Create your views here.

# トップページ
def top_page(request):
    # ユーザーデータ取得
    user = request.user

    if user.is_superuser:
        return redirect(settings.ADMIN_URL)  # 管理者はDjango管理画面へ

    # ユーザーデータの中の役割情報を初期値Noneで取得
    role = getattr(user, 'role', None)

    if role == 'player':
        return render(request, 'players/top_player.html')
    elif role == 'manager':
        return render(request, 'players/top_manager.html')
    elif role == 'coach':
        return render(request, 'players/top_coach.html')
    elif role == 'director':
        return render(request, 'players/top_director.html')
    else:
        return render(request, 'players/top_unknown.html')  # 未定義のロール用

# 監督・コーチ ユーザー追加・削除・一覧表示画面
@coach_or_director_required
def user_list(request):
    users = CustomUser.objects.exclude(is_superuser=True)
    return render(request, 'players/user_list.html', {'users': users})

@coach_or_director_required
def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'players/user_form.html', {'form': form})

def create_member(request):
    if request.user.role != 'director':
        return render(request, 'players/unauthorized.html')

    if request.method == 'POST':
        form = MemberCreationForm(request.POST)
        if form.is_valid():
            user = CustomUser.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                role=form.cleaned_data['role'],
            )
            StudentProfile.objects.create(
                user=user,
                grade=form.cleaned_data['grade'],
                class_number=form.cleaned_data['class_number'],
                joined_at=form.cleaned_data['joined_at'],
                status='active',
            )
            return redirect('top_director')
    else:
        form = MemberCreationForm()
    return render(request, 'players/create_member.html', {'form': form})


@coach_or_director_required
def user_delete(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'players/user_confirm_delete.html', {'user': user})


# 記録確認画面  選手向け
def player_records(request):
    records = MeasurementRecord.objects.filter(player_user=request.user).order_by('-measured_at')
    return render(request, 'players/player_records.html', {'records': records})
# 部員選択・記録入力画面  マネージャー向け
def record_input(request):
    # 部員選択・記録入力画面（フォームは後で追加）
    return render(request, 'players/record_input.html')
# 全部員の記録一覧  コーチ・監督向け
def all_players_records(request):
    records = MeasurementRecord.objects.all().order_by('-measured_at')
    return render(request, 'players/all_players_records.html', {'records': records})
