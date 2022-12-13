from functools import wraps
from flask_login import current_user
from PrivateClinics.models import UserRole
from flask import redirect


def anonymous_user(f):
    def decorated_func(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect('/')

        return f(*args, **kwargs)

    return decorated_func


def doctor_user(f):
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_role not in [UserRole.DOCTOR]:
            return redirect('/')
        return f(*args, **kwargs)

    return decorated_func


def nurse_user(f):
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_role not in [UserRole.DOCTOR, UserRole.NURSE]:
            return redirect('/')
        return f(*args, **kwargs)

    return decorated_func


def employee_user(f):
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_role not in [UserRole.DOCTOR, UserRole.NURSE, UserRole.EMPLOYEE]:
            return redirect('/')
        return f(*args, **kwargs)

    return decorated_func
