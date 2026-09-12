import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'khoa-bi-mat-mac-dinh-chi-dung-de-dev')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/quanbia_db')
    WTF_CSRF_ENABLED = True

    # Ngưỡng cảnh báo tồn kho mặc định (nếu nguyên liệu không đặt riêng)
    DEFAULT_MIN_STOCK = 5
