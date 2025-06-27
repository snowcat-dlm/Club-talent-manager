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