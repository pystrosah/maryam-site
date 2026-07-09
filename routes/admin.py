import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from models import (
    get_all_users, get_all_courses_admin, get_all_enrollments, get_all_messages,
    get_course, get_db, get_enrollment_stats
)
from utils import admin_required
from config import Config

admin_bp = Blueprint('admin', __name__)

def allowed_file(filename):
    """بررسی پسوند مجاز فایل"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """ذخیره فایل آپلود شده"""
    if file and allowed_file(file.filename):
        # ایجاد نام یکتا برای فایل
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # ذخیره فایل
        filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # برگرداندن مسیر نسبی برای ذخیره در دیتابیس
        return f"/static/uploads/courses/{unique_filename}"
    return None

@admin_bp.route('/admin')
@admin_required
def dashboard():
    users = get_all_users()
    courses = get_all_courses_admin()
    enrollments = get_all_enrollments()
    stats = get_enrollment_stats()
    
    total_enrollments = len(enrollments)
    pending_enrollments = len([e for e in enrollments if e['status'] == 'pending'])
    paid_enrollments = len([e for e in enrollments if e['status'] == 'paid'])
    completed_enrollments = len([e for e in enrollments if e['status'] == 'completed'])
    cancelled_enrollments = len([e for e in enrollments if e['status'] == 'cancelled'])
    
    stats_dict = {
        'total_users': len(users),
        'total_courses': len(courses),
        'total_enrollments': total_enrollments,
        'pending_enrollments': pending_enrollments,
        'paid_enrollments': paid_enrollments,
        'completed_enrollments': completed_enrollments,
        'cancelled_enrollments': cancelled_enrollments
    }
    
    recent_enrollments = enrollments[:5] if enrollments else []
    
    return render_template('admin/dashboard.html', 
                         stats=stats_dict, 
                         users=users[:5], 
                         enrollments=recent_enrollments)

@admin_bp.route('/admin/courses')
@admin_required
def courses():
    courses = get_all_courses_admin()
    return render_template('admin/courses.html', courses=courses)

@admin_bp.route('/admin/course/add', methods=['GET', 'POST'])
@admin_required
def add_course():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        description = request.form.get('description')
        price = request.form.get('price')
        teacher = request.form.get('teacher')
        capacity = request.form.get('capacity')
        
        # پردازش آپلود عکس
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                saved_path = save_uploaded_file(file)
                if saved_path:
                    image_path = saved_path
                else:
                    flash('فرمت فایل مجاز نیست. فقط: png, jpg, jpeg, gif, webp, svg', 'danger')
                    return render_template('admin/course_form.html')
        
        if not all([title, category, price]):
            flash('فیلدهای اجباری را پر کنید', 'danger')
            return render_template('admin/course_form.html')
        
        conn = get_db()
        conn.execute('''INSERT INTO courses (title, category, description, price, teacher, capacity, image)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (title, category, description, price, teacher, capacity or 20, image_path))
        conn.commit()
        conn.close()
        flash('دوره با موفقیت اضافه شد', 'success')
        return redirect(url_for('admin.courses'))
    
    return render_template('admin/course_form.html')

@admin_bp.route('/admin/course/<int:course_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_course(course_id):
    course = get_course(course_id)
    if not course:
        flash('دوره پیدا نشد', 'danger')
        return redirect(url_for('admin.courses'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        description = request.form.get('description')
        price = request.form.get('price')
        teacher = request.form.get('teacher')
        capacity = request.form.get('capacity')
        
        # پردازش آپلود عکس جدید
        image_path = course['image']  # نگه داشتن عکس قبلی
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                saved_path = save_uploaded_file(file)
                if saved_path:
                    # حذف عکس قبلی اگر وجود داشت
                    if course['image'] and os.path.exists(os.path.join(Config.BASE_DIR, course['image'].lstrip('/'))):
                        try:
                            os.remove(os.path.join(Config.BASE_DIR, course['image'].lstrip('/')))
                        except:
                            pass
                    image_path = saved_path
                else:
                    flash('فرمت فایل مجاز نیست. فقط: png, jpg, jpeg, gif, webp, svg', 'danger')
                    return render_template('admin/course_form.html', course=course)
        
        conn = get_db()
        conn.execute('''UPDATE courses 
                       SET title = ?, category = ?, description = ?, 
                           price = ?, teacher = ?, capacity = ?, image = ?
                       WHERE id = ?''',
                    (title, category, description, price, teacher, capacity, image_path, course_id))
        conn.commit()
        conn.close()
        flash('دوره با موفقیت ویرایش شد', 'success')
        return redirect(url_for('admin.courses'))
    
    return render_template('admin/course_form.html', course=course)

@admin_bp.route('/admin/course/<int:course_id>/delete', methods=['POST'])
@admin_required
def delete_course(course_id):
    course = get_course(course_id)
    if course:
        # حذف عکس دوره اگر وجود داشت
        if course['image'] and os.path.exists(os.path.join(Config.BASE_DIR, course['image'].lstrip('/'))):
            try:
                os.remove(os.path.join(Config.BASE_DIR, course['image'].lstrip('/')))
            except:
                pass
    
    conn = get_db()
    conn.execute('DELETE FROM courses WHERE id = ?', (course_id,))
    conn.commit()
    conn.close()
    flash('دوره با موفقیت حذف شد', 'success')
    return redirect(url_for('admin.courses'))

# سایر روت‌ها مانند قبل...
@admin_bp.route('/admin/user/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    if user_id == session['user_id']:
        flash('نمی‌توانید خودتان را غیرفعال کنید', 'danger')
        return redirect(url_for('admin.users'))
    
    conn = get_db()
    user = conn.execute('SELECT is_active FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        new_status = 0 if user['is_active'] else 1
        conn.execute('UPDATE users SET is_active = ? WHERE id = ?', (new_status, user_id))
        conn.commit()
        flash('وضعیت کاربر با موفقیت تغییر کرد', 'success')
    conn.close()
    return redirect(url_for('admin.users'))

@admin_bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    if user_id == session['user_id']:
        flash('نمی‌توانید خودتان را حذف کنید', 'danger')
        return redirect(url_for('admin.users'))
    
    conn = get_db()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    flash('کاربر با موفقیت حذف شد', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/admin/enrollments')
@admin_required
def enrollments():
    enrollments = get_all_enrollments()
    return render_template('admin/enrollments.html', enrollments=enrollments)

@admin_bp.route('/admin/enrollment/<int:enrollment_id>/update', methods=['POST'])
@admin_required
def update_enrollment(enrollment_id):
    status = request.form.get('status')
    
    conn = get_db()
    conn.execute('UPDATE enrollments SET status = ? WHERE id = ?', (status, enrollment_id))
    conn.commit()
    conn.close()
    flash('وضعیت ثبت‌نام با موفقیت بروزرسانی شد', 'success')
    return redirect(url_for('admin.enrollments'))

@admin_bp.route('/admin/messages')
@admin_required
def messages():
    messages = get_all_messages()
    return render_template('admin/messages.html', messages=messages)

@admin_bp.route('/admin/message/<int:message_id>/reply', methods=['POST'])
@admin_required
def reply_message(message_id):
    reply = request.form.get('reply')
    
    if reply:
        conn = get_db()
        conn.execute('''UPDATE messages 
                       SET admin_reply = ?, is_read = 1 
                       WHERE id = ?''',
                    (reply, message_id))
        conn.commit()
        conn.close()
        flash('پاسخ شما با موفقیت ارسال شد', 'success')
    else:
        flash('لطفاً متن پاسخ را وارد کنید', 'danger')
    
    return redirect(url_for('admin.messages'))

# اضافه کردن روت users
@admin_bp.route('/admin/users')
@admin_required
def users():
    users = get_all_users()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/course/<int:course_id>/toggle', methods=['POST'])
@admin_required
def toggle_course(course_id):
    conn = get_db()
    course = conn.execute('SELECT is_active FROM courses WHERE id = ?', (course_id,)).fetchone()
    if course:
        new_status = 0 if course['is_active'] else 1
        conn.execute('UPDATE courses SET is_active = ? WHERE id = ?', (new_status, course_id))
        conn.commit()
        flash('وضعیت دوره با موفقیت تغییر کرد', 'success')
    conn.close()
    return redirect(url_for('admin.courses'))