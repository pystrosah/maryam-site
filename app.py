from flask import Flask
from config import Config
from models import init_db
from utils import format_price
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    
    # ایجاد پوشه آپلود
    Config.init_upload_folder()
    
    # ثبت فیلترها
    app.jinja_env.filters['format_price'] = format_price
    
    # ثبت Blueprint ها
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.user import user_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    
    # context processor
    @app.context_processor
    def utility_processor():
        from models import get_user_by_id
        return dict(get_user_by_id=get_user_by_id)
    
    return app

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 راه‌اندازی کانون فرهنگی مریم")
    print("=" * 60)
    
    # ایجاد دیتابیس
    init_db()
    print("✅ دیتابیس راه‌اندازی شد")
    
    # ایجاد پوشه آپلود
    Config.init_upload_folder()
    print("✅ پوشه آپلود ساخته شد")
    
    app = create_app()
    print("✅ برنامه با موفقیت راه‌اندازی شد!")
    print("📌 آدرس: http://localhost:5000")
    print("👤 ادمین: admin / admin123")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)