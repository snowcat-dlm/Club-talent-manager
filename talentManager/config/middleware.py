from django.conf import settings
from django.shortcuts import redirect
import re

EXEMPT_URLS = [
    re.compile(settings.LOGIN_URL.lstrip('/')),      # 例: accounts/login/
    # re.compile(r'^admin/login/$'),                   # 管理画面ログイン
    # re.compile(r'^admin/.*'),                        # admin画面全体（任意）
    # re.compile(r'^accounts/signup/$'),               # サインアップページがあれば
    # re.compile(r'^api/.*'),                        # APIを除外したい場合
]

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info.lstrip('/')
        if not request.user.is_authenticated:
            if not any(pattern.match(path) for pattern in EXEMPT_URLS):
                return redirect(settings.LOGIN_URL)
        return self.get_response(request)
