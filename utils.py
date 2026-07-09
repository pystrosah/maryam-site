from functools import wraps
from flask import session, flash, redirect, url_for
from models import get_user_by_id

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('لطفاً ابتدا وارد شوید', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('لطفاً ابتدا وارد شوید', 'warning')
            return redirect(url_for('login'))
        user = get_user_by_id(session['user_id'])
        if not user or user['role'] != 'admin':
            flash('شما دسترسی ادمین ندارید', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def format_price(value):
    try:
        return f"{int(value):,}"
    except:
        return str(value)