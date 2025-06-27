from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages
from django.utils import timezone
from accounts.models import CustomUser
from .decorators import coach_or_director_required, coach_required, manager_required    # @coach_required, @coach_or_director_requiredの設定をインポート
from django.conf import settings                      # settings.pyをインポート
from players.models import StudentProfile, PlayerProfile, MeasurementRecord, ApprovalStatus
from players.forms import MemberCreationForm, StudentProfileForm, PlayerProfileForm
from players.forms import MeasurementForm, MeasurementItemFormSet




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

# 記録入力画面  マネージャー向け
@manager_required
def create_measurement_record(request):
    if request.method == 'POST':
        form = MeasurementForm(request.POST)
        formset = MeasurementItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            record = form.save(commit=False)
            record.created_by = request.user
            record.status = 'awaiting_player_approval'
            record.save()
            formset.instance = record
            formset.save()

            # 承認フロー作成（選手）
            ApprovalStatus.objects.create(
                record=record,
                approver=record.player.student.user,
                role='player'
            )

            # 承認フロー作成（全コーチ）
            coaches = CustomUser.objects.filter(role='coach')
            coach_approvals = [
                ApprovalStatus(
                    record=record,
                    approver=coach,
                    role='coach'
                )
                for coach in coaches
            ]
            ApprovalStatus.objects.bulk_create(coach_approvals)

            return redirect('measurement_record_list')
    else:
        form = MeasurementForm()
        formset = MeasurementItemFormSet()

    return render(request, 'players/manager/create_record.html', {
        'form': form,
        'formset': formset,
    })
# 記録一覧画面  マネージャー向け
@manager_required
def measurement_record_list(request):
    records = MeasurementRecord.objects.filter(created_by=request.user).order_by('-measured_at')
    return render(request, 'players/manager/record_list.html', {'records': records})
# 承認ステータス一覧  マネージャー向け
@manager_required
def approval_status_list(request):
    records = MeasurementRecord.objects.filter(created_by=request.user).prefetch_related('approvalstatus_set')
    return render(request, 'players/manager/approval_status_list.html', {'records': records})


# コーチ向けの承認待ち記録一覧
@coach_required
def coach_approval_list(request):
    records = MeasurementRecord.objects.filter(
        status='awaiting_coach_approval',
        approvalstatus__approver=request.user,
        approvalstatus__role='coach',
        approvalstatus__status='pending'
    ).distinct()
    return render(request, 'players/coach/approval_list.html', {'records': records})

# コーチによる記録承認処理
@coach_required
def approve_record_as_coach(request, record_id):
    if request.method == 'POST':
        record = get_object_or_404(MeasurementRecord, id=record_id)
        approval = get_object_or_404(
            ApprovalStatus,
            record=record,
            approver=request.user,
            role='coach'
        )
        approval.status = 'approved'
        approval.approved_at = timezone.now()
        approval.save()

        # レコード全体のステータス更新
        record.status = 'approved'
        record.save()

        return redirect('coach_approval_list')

# 全部員の記録一覧  コーチ・監督向け
STATUS_CHOICES = [
    ('draft', '下書き'),
    ('awaiting_player_approval', '選手承認待ち'),
    ('awaiting_coach_approval', 'コーチ承認待ち'),
    ('approved', '承認済み'),
]
@coach_or_director_required
def all_players_records(request):
    records = MeasurementRecord.objects.select_related('player__student__user').all().order_by('-measured_at')
    players = PlayerProfile.objects.select_related('student__user').all()

    # フィルター取得
    player_id = request.GET.get('player')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # フィルター適用
    if player_id:
        records = records.filter(player_id=player_id)

    if status:
        records = records.filter(status=status)

    if date_from:
        records = records.filter(measured_at__gte=date_from)

    if date_to:
        records = records.filter(measured_at__lte=date_to)

    return render(request, 'players/all_players_records.html', {
        'records': records,
        'players': players,
        'selected_player': player_id,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': STATUS_CHOICES,
    })
