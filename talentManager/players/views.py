from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages
from accounts.models import CustomUser
from .decorators import coach_or_director_required    # @coach_or_director_requiredの設定をインポート
from django.conf import settings                      # settings.pyをインポート
from players.models import StudentProfile, PlayerProfile, MeasurementRecord
from players.forms import MemberCreationForm, StudentProfileForm, PlayerProfileForm




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
# 部員一覧画面
@coach_or_director_required
def user_list(request):
    users = CustomUser.objects.exclude(is_superuser=True)
    return render(request, 'players/user_list.html', {'users': users})
# 部員追加画面
@coach_or_director_required
def user_create(request):
    if request.method == 'POST':
        user_form = MemberCreationForm(request.POST)
        student_form = StudentProfileForm(request.POST)
        player_form = PlayerProfileForm(request.POST)
        role = user_form.data.get('role')

        # ロールに応じてバリデーション対象を決定
        needs_student = role in ['player', 'manager']
        needs_player = role == 'player'
        # バリデーションチェック
        user_valid = user_form.is_valid()
        student_valid = not needs_student or student_form.is_valid()
        player_valid = not needs_player or player_form.is_valid()

        if user_valid and student_valid and player_valid:
            # カスタムユーザー作成
            user = CustomUser.objects.create_user(
                username=user_form.cleaned_data['username'],
                email=user_form.cleaned_data['email'],
                password=user_form.cleaned_data['password'],
                role=user_form.cleaned_data['role'],
            )
            # カスタムユーザー作成時にロールが学生（playerまたはmanager）ならStudentProfile作成
            if needs_student:
                student = StudentProfile.objects.create(
                    user=user,
                    **student_form.cleaned_data
                )
                # カスタムユーザー作成時にロールがplayerならPlayerProfileも作成
                if needs_player:
                    PlayerProfile.objects.create(
                        student=student,
                        **player_form.cleaned_data
                    )
            
            messages.success(request, f"ユーザー「{user.username}」を作成しました。")
            return redirect('user_list')
    else:
        user_form = MemberCreationForm()
        student_form = StudentProfileForm()
        player_form = PlayerProfileForm()

    return render(request, 'players/user_create.html', {
        'user_form': user_form,
        'student_form': student_form,
        'player_form': player_form,
    })
# 部員編集画面
@coach_or_director_required
def user_edit(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    try:
        student = user.studentprofile
    except StudentProfile.DoesNotExist:
        student = None

    try:
        player = student.playerprofile if student else None
    except PlayerProfile.DoesNotExist:
        player = None

    if request.method == 'POST':
        user_form = MemberCreationForm(request.POST, instance=user)
        student_form = StudentProfileForm(request.POST, instance=student) if student else StudentProfileForm(request.POST)
        player_form = PlayerProfileForm(request.POST, instance=player) if player else PlayerProfileForm(request.POST)

        role = request.POST.get('role')

        needs_student = role in ['player', 'manager']
        needs_player = role == 'player'

        if user_form.is_valid() and (not needs_student or student_form.is_valid()) and (not needs_player or player_form.is_valid()):
            user_form.save()

            if needs_student:
                student = student_form.save(commit=False)
                student.user = user
                student.save()

                if needs_player:
                    player = player_form.save(commit=False)
                    player.student = student
                    player.save()

            return redirect('user_list')
    else:
        user_form = MemberCreationForm(instance=user)
        student_form = StudentProfileForm(instance=student)
        player_form = PlayerProfileForm(instance=player)

    return render(request, 'players/user_edit.html', {
        'user_form': user_form,
        'student_form': student_form,
        'player_form': player_form,
        'user_id': user_id
    })
# 部員削除画面
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
