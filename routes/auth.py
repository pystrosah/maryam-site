from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import get_user, get_user_by_id, get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user(username)
        if user and check_password_hash(user['password_hash'], password):
            if user['is_active']:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash(f'خوش آمدید {user["full_name"]}', 'success')
                if user['role'] == 'admin':
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('user.dashboard'))
            else:
                flash('حساب کاربری شما غیرفعال است', 'danger')
        else:
            flash('نام کاربری یا رمز عبور اشتباه است', 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        
        if not all([username, password, full_name, phone]):
            flash('تمامی فیلدهای اجباری را پر کنید', 'danger')
            return render_template('register.html')
        
        if get_user(username):
            flash('این نام کاربری قبلاً ثبت شده است', 'danger')
            return render_template('register.html')
        
        conn = get_db()
        password_hash = generate_password_hash(password)
        conn.execute('''INSERT INTO users (username, password_hash, full_name, phone, email)
                       VALUES (?, ?, ?, ?, ?)''',
                    (username, password_hash, full_name, phone, email))
        conn.commit()
        conn.close()
        
        flash('ثبت‌نام با موفقیت انجام شد. حالا وارد شوید', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('شما خارج شدید', 'info')
    return redirect(url_for('main.index'))