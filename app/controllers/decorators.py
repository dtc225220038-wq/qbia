from functools import wraps
from flask import abort
from flask_login import current_user


def roles_required(*roles):
    """Chỉ cho phép các vai trò được liệt kê truy cập route."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator
