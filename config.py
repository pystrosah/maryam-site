import os

class Config:
    SECRET_KEY = 'kanoon_maryam_secret_key_1404'
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'instance', 'kanoon.db')
    DEBUG = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # تنظیمات آپلود
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'courses')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
    
    # ایجاد پوشه آپلود اگر وجود ندارد
    @staticmethod
    def init_upload_folder():
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)