from django.contrib.auth.decorators import user_passes_test

def coach_or_director_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and getattr(u, 'role', None) in ['coach', 'director']
    )(view_func)
