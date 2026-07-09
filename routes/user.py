from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import (
    get_user_by_id, get_user_enrollments, get_user_messages,
    get_course, get_db
)
from utils import login_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    enrollments = get_user_enrollments(user_id)
    my_courses = [e for e in enrollments if e['status'] in ['paid', 'completed']]
    pending_courses = [e for e in enrollments if e['status'] == 'pending']
    messages = get_user_messages(user_id)
    
    return render_template('dashboard.html', 
                         my_courses=my_courses, 
                         pending_courses=pending_courses,
                         messages=messages)

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    user = get_user_by_id(user_id)
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        
        conn = get_db()
        conn.execute('''UPDATE users 
                       SET full_name = ?, phone = ?, email = ? 
                       WHERE id = ?''',
                    (full_name, phone, email, user_id))
        conn.commit()
        conn.close()
        
        flash('اطلاعات با موفقیت بروزرسانی شد', 'success')
        return redirect(url_for('user.profile'))
    
    return render_template('profile.html', user=user)

@user_bp.route('/my-courses')
@login_required
def my_courses():
    user_id = session['user_id']
    enrollments = get_user_enrollments(user_id)
    return render_template('my_courses.html', enrollments=enrollments)

@user_bp.route('/course/<int:course_id>')
@login_required
def course_detail(course_id):
    course = get_course(course_id)
    if not course:
        flash('دوره پیدا نشد', 'danger')
        return redirect(url_for('main.courses'))
    
    user_id = session['user_id']
    conn = get_db()
    enrollment = conn.execute('''SELECT * FROM enrollments 
                                WHERE user_id = ? AND course_id = ?''',
                             (user_id, course_id)).fetchone()
    conn.close()
    
    return render_template('course_detail.html', course=course, enrollment=enrollment)

@user_bp.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_course(course_id):
    user_id = session['user_id']
    course = get_course(course_id)
    
    if not course:
        flash('دوره پیدا نشد', 'danger')
        return redirect(url_for('main.courses'))
    
    conn = get_db()
    existing = conn.execute('''SELECT * FROM enrollments 
                              WHERE user_id = ? AND course_id = ?''',
                           (user_id, course_id)).fetchone()
    
    if existing:
        flash('شما قبلاً در این دوره ثبت‌نام کرده‌اید', 'warning')
        conn.close()
        return redirect(url_for('user.my_courses'))
    
    conn.execute('''INSERT INTO enrollments (user_id, course_id, status, payment_method)
                   VALUES (?, ?, 'pending', 'cash')''',
                (user_id, course_id))
    conn.commit()
    conn.close()
    
    flash('درخواست ثبت‌نام شما با موفقیت ثبت شد. منتظر تایید ادمین باشید.', 'success')
    return redirect(url_for('user.my_courses'))

@user_bp.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    user_id = session['user_id']
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        content = request.form.get('content')
        
        if subject and content:
            conn = get_db()
            conn.execute('''INSERT INTO messages (user_id, subject, content)
                           VALUES (?, ?, ?)''',
                        (user_id, subject, content))
            conn.commit()
            conn.close()
            flash('پیام شما با موفقیت ارسال شد', 'success')
            return redirect(url_for('user.messages'))
    
    user_messages = get_user_messages(user_id)
    return render_template('messages.html', messages=user_messages)