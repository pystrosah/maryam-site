import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

def get_db():
    from config import Config
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # جدول کاربران
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )''')
    
    # جدول دوره‌ها با فیلد image
    c.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL,
        teacher TEXT,
        start_date TIMESTAMP,
        end_date TIMESTAMP,
        capacity INTEGER DEFAULT 20,
        image TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # جدول ثبت‌نام‌ها
    c.execute('''CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        status TEXT DEFAULT 'pending',
        payment_method TEXT DEFAULT 'cash',
        payment_amount INTEGER,
        payment_date TIMESTAMP,
        enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (course_id) REFERENCES courses (id)
    )''')
    
    # جدول پیام‌ها
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        content TEXT NOT NULL,
        is_read BOOLEAN DEFAULT 0,
        admin_reply TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    
    # ایجاد ادمین پیش‌فرض
    admin = c.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
    if not admin:
        c.execute('''INSERT INTO users (username, password_hash, full_name, phone, role)
                    VALUES (?, ?, ?, ?, ?)''',
                 ('admin', generate_password_hash('admin-kanoon-maryam@3541232'), 'مدیر کانون', '09123456789', 'admin'))
        conn.commit()
    
    # ✅ حذف بخش ساخت دوره‌های نمونه
    # دیگر دوره‌های پیش‌فرض ساخته نمی‌شوند
    
    conn.close()
    
# توابع دیتابیس
def get_user(username):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def get_all_users():
    conn = get_db()
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return users

def get_all_courses():
    conn = get_db()
    courses = conn.execute('SELECT * FROM courses WHERE is_active = 1 ORDER BY created_at DESC').fetchall()
    conn.close()
    return courses

def get_all_courses_admin():
    conn = get_db()
    courses = conn.execute('SELECT * FROM courses ORDER BY created_at DESC').fetchall()
    conn.close()
    return courses

def get_course(course_id):
    conn = get_db()
    course = conn.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
    conn.close()
    return course

def get_user_enrollments(user_id):
    conn = get_db()
    enrollments = conn.execute('''
        SELECT e.*, c.title as course_title, c.category, c.teacher, c.image 
        FROM enrollments e 
        JOIN courses c ON e.course_id = c.id 
        WHERE e.user_id = ? 
        ORDER BY e.enrolled_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return enrollments

def get_all_enrollments():
    conn = get_db()
    enrollments = conn.execute('''
        SELECT e.*, u.full_name as user_name, u.username, c.title as course_title 
        FROM enrollments e 
        JOIN users u ON e.user_id = u.id 
        JOIN courses c ON e.course_id = c.id 
        ORDER BY e.enrolled_at DESC
    ''').fetchall()
    conn.close()
    return enrollments

def get_user_messages(user_id):
    conn = get_db()
    messages = conn.execute('SELECT * FROM messages WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()
    conn.close()
    return messages

def get_all_messages():
    conn = get_db()
    messages = conn.execute('''
        SELECT m.*, u.full_name, u.username 
        FROM messages m 
        JOIN users u ON m.user_id = u.id 
        ORDER BY m.created_at DESC
    ''').fetchall()
    conn.close()
    return messages

def get_enrollment_stats():
    """دریافت آمار ثبت‌نام‌ها برای داشبورد"""
    conn = get_db()
    stats = conn.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) as paid,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled
        FROM enrollments
    ''').fetchone()
    conn.close()
    return stats