from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps

# このデコレーターは、ユーザーが認証されていて、かつ役割が 'coach' または 'director' の場合にのみビューを実行します。
def coach_or_director_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and getattr(u, 'role', None) in ['coach', 'director']
    )(view_func)

# このデコレーターは、ユーザーが認証されていて、かつ役割が 'coach' の場合にのみビューを実行します。
def coach_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'coach':
            return view_func(request, *args, **kwargs)
        raise PermissionDenied  # 403 Forbidden
    return _wrapped_view

# このデコレーターは、ユーザーが認証されていて、かつ役割が 'manager' の場合にのみビューを実行します。
def manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'manager':
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view


# このデコレーターは、ユーザーが認証されていて、かつロールのいずれかを持つ場合にのみビューを実行します。
# role一覧 => player, manager, coach, director
def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                # 管理者（superuser）は常に許可
                if request.user.is_superuser:
                    return view_func(request, *args, **kwargs)

                # 通常ユーザーのロールチェック
                if hasattr(request.user, 'role') and request.user.role in allowed_roles:
                    return view_func(request, *args, **kwargs)

            raise PermissionDenied
        return _wrapped_view
    return decorator
