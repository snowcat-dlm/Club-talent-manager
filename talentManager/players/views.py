from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.conf import settings  #settings.pyをインポート


# Create your views here.

# トップページ
@login_required
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
# # トップページ V1
# @login_required
# def top_page(request):
#     return render(request, 'players/top_page.html')

# 記録確認画面  選手向け
@login_required
def player_records(request):
    records = MeasurementRecord.objects.filter(player_user=request.user).order_by('-measured_at')
    return render(request, 'players/player_records.html', {'records': records})
# 部員選択・記録入力画面  マネージャー向け
def record_input(request):
    # 部員選択・記録入力画面（フォームは後で追加）
    return render(request, 'players/record_input.html')
# 全部員の記録一覧  コーチ・監督向け
@login_required
def all_players_records(request):
    records = MeasurementRecord.objects.all().order_by('-measured_at')
    return render(request, 'players/all_players_records.html', {'records': records})
