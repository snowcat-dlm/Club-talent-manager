from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages
from django.utils import timezone
from accounts.models import CustomUser
from .decorators import coach_or_director_required, coach_required, manager_required, role_required    # @coach_required, @coach_or_director_requiredの設定をインポート
from django.conf import settings                      # settings.pyをインポート
from players.models import StudentProfile, PlayerProfile, MeasurementRecord, ApprovalStatus
from players.forms import MemberCreationForm, StudentProfileForm, PlayerProfileForm, MeasurementForm, MeasurementItemFormSet, RejectionForm
from .models import MeasurementItem, MeasurementRecord, ApprovalStatus
import plotly.graph_objects as go
import plotly.offline as opy

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
@role_required('player')
def my_record_list(request):
    records = MeasurementRecord.objects.filter(
        player__student__user=request.user
    ).prefetch_related('items', 'approvalstatus_set').order_by('-measured_at')
    return render(request, 'players/player/my_record_list.html', {'records': records})
# 記録承認画面  選手向け
@role_required('player')
def approve_measurement_record(request, record_id):
    if request.method == 'POST':
        approval = ApprovalStatus.objects.filter(
            record_id=record_id,
            approver=request.user,
            role='player',
            status='pending'
        ).first()
        if approval:
            approval.status = 'approved'
            approval.approved_at = timezone.now()
            approval.save()

            # レコード全体のステータス変更
            record = approval.record
            record.status = 'awaiting_coach_approval'
            record.save()

    return redirect('my_record_list')

# 記録否認画面  選手向け
@role_required('player')
def reject_measurement_record(request, record_id):
    approval = get_object_or_404(
        ApprovalStatus,
        record_id=record_id,
        approver=request.user,
        role='player',
        status='pending'
    )

    if request.method == 'POST':
        form = RejectionForm(request.POST)
        if form.is_valid():
            approval.status = 'rejected'
            approval.comment = form.cleaned_data['comment']
            approval.approved_at = timezone.now()
            approval.save()

            # レコードの状態は変えずにそのまま（マネージャーが再作成）

            return redirect('my_record_list')
    else:
        form = RejectionForm()

    return render(request, 'players/player/reject_record.html', {
        'form': form,
        'record': approval.record
    })



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
# コーチによる記録否認処理
@role_required('coach')
def reject_record_as_coach(request, record_id):
    approval = get_object_or_404(
        ApprovalStatus,
        record_id=record_id,
        approver=request.user,
        role='coach',
        status='pending'
    )

    if request.method == 'POST':
        form = RejectionForm(request.POST)
        if form.is_valid():
            approval.status = 'rejected'
            approval.comment = form.cleaned_data['comment']
            approval.approved_at = timezone.now()
            approval.save()

            # レコードのステータスは manager の判断で修正される
            return redirect('coach_approval_list')
    else:
        form = RejectionForm()

    return render(request, 'players/coach/reject_record.html', {
        'form': form,
        'record': approval.record
    })

# 全部員の記録一覧  コーチ・監督向け
STATUS_CHOICES = [
    ('draft', '下書き'),
    ('awaiting_player_approval', '選手承認待ち'),
    ('awaiting_coach_approval', 'コーチ承認待ち'),
    ('approved', '承認済み'),
]

@coach_or_director_required
def all_players_records(request):
    import plotly.graph_objs as go
    import plotly.offline as opy
    from .models import MeasurementRecord, MeasurementItem, PlayerProfile

    #データ取得（プレイヤー、測定レコード、測定アイテムのカテゴリー）
    players = PlayerProfile.objects.select_related('student__user').all()
    records = MeasurementRecord.objects.select_related('player__student__user').prefetch_related('items').all()
    categories = MeasurementItem.objects.values_list('category', flat=True).distinct()
    item_names = MeasurementItem.objects.values_list('item_name', flat=True).distinct()

    # --- フィルター取得 ---
    player_id = request.GET.get('player')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    category = request.GET.get('category')
    item_name = request.GET.get('item_name')

    # --- フィルター適用 ---
    if player_id:
        records = records.filter(player_id=player_id)
    if status:
        records = records.filter(status=status)
    if date_from:
        records = records.filter(measured_at__gte=date_from)
    if date_to:
        records = records.filter(measured_at__lte=date_to)

    # --- グラフ生成 ---
    traces = []
    filtered_players = players.filter(id=player_id) if player_id else players

    for player in filtered_players:
        player_records = records.filter(player=player).order_by('measured_at')
        dates, values = [], []
        for record in player_records:
            item = record.items.filter(item_name=item_name) if item_name else record.items.all()
            item = item.filter(category=category).first() if category else item.first() 
            if item:
                dates.append(record.measured_at)
                values.append(item.value)
        if dates:
            trace = go.Scatter(
                x=dates,
                y=values,
                mode='lines+markers',
                name=player.student.user.last_name + player.student.user.first_name
            )
            traces.append(trace)

    plot_div = None
    if traces:
        layout = go.Layout(
            title=f"{item_name or category or '記録'} の推移",
            xaxis=dict(title='測定日'),
            yaxis=dict(title='値'),
            height=400
        )
        figure = go.Figure(data=traces, layout=layout)
        plot_div = opy.plot(figure, auto_open=False, output_type='div')

    return render(request, 'players/all_players_records.html', {
        'records': records,
        'players': players,
        'selected_player': player_id,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': STATUS_CHOICES,
        'categories': categories,
        'category': category,
        'item_names': item_names,
        'item_name': item_name,
        'plot_div': plot_div,
    })


""" @coach_or_director_required
def all_players_records(request):
    records = MeasurementRecord.objects.select_related('player__student__user').all().order_by('-measured_at')
    players = PlayerProfile.objects.select_related('student__user').all()
    items = MeasurementItem.objects.select_related('records__player__student__user').all()


    # フィルター取得
    player_id = request.GET.get('player')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    category = request.GET.get('category')  # 測定カテゴリ（例：走力）
    item_name = request.GET.get('item_name')  # 測定項目名（例：50m走）
    value = request.GET.get('value')  # 計測値（数値）
    unit = request.GET.get('unit')  # 単位（例：秒, km/h）

    # フィルター適用
    if player_id:
        records = records.filter(player_id=player_id)

    if status:
        records = records.filter(status=status)

    if date_from:
        records = records.filter(measured_at__gte=date_from)

    if date_to:
        records = records.filter(measured_at__lte=date_to)

    if category:
        items = items.filter(category=category)  # 測定カテゴリ（例：走力）

    # グラフ描画
    traces = []
    filtered_players = players.filter(id=player_id) if player_id else players

    for player in filtered_players:
        player_records = records.filter(player=player).order_by('measured_at')
        records_items = items.filter(record=player_records)
        dates = []
        values = []
        for item in records_items:
            item = MeasurementItem.objects.filter(category=category, item_name='走力').first()
            if item:
                dates.append(record.measured_at)
                values.append(item.value)
        if dates:
            trace = go.Scatter(
                x=dates,
                y=values,
                mode='lines+markers',
                name=player.student.user.username
            )
            traces.append(trace)

    plot_div = None
    if traces:
        layout = go.Layout(
            title='50m走の推移',
            xaxis=dict(title='測定日'),
            yaxis=dict(title='秒'),
            height=400
        )
        figure = go.Figure(data=traces, layout=layout)
        plot_div = opy.plot(figure, auto_open=False, output_type='div')
    
    print(plot_div)
    
    return render(request, 'players/all_players_records.html', {
        'records': records,
        'players': players,
        'selected_player': player_id,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': STATUS_CHOICES,
        'category': category,
        'item_name': item_name,
        'value': value,
        'unit': unit,
        'plot_div': plot_div,
    })
 """