"""
Conftest cho bộ test module Order (PBI-001, PBI-002) - T-007.

Dùng mongomock để giả lập MongoDB (không cần cài/mở MongoDB thật),
nhưng vẫn chạy qua đúng code thật của app (models + controllers + Flask).
"""
import sys
import os
import pytest
import mongomock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import mongo, hash_password
from app.models.user import ROLE_ADMIN, ROLE_STAFF, ROLE_KITCHEN


class TestConfig:
    SECRET_KEY = 'test-secret-key'
    MONGO_URI = 'mongodb://localhost:27017/quanbia_test'
    WTF_CSRF_ENABLED = False  # tắt CSRF để test POST form không cần token
    TESTING = True


@pytest.fixture()
def app():
    flask_app = create_app(TestConfig)

    # Thay driver MongoDB thật bằng mongomock (in-memory, không cần server thật)
    mongo.cx = mongomock.MongoClient()
    mongo.db = mongo.cx['quanbia_test']

    with flask_app.app_context():
        _seed_minimal_data()

    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


def _seed_minimal_data():
    """Seed vừa đủ dữ liệu để test module Order chạy được."""
    mongo.db.users.insert_one({
        'username': 'staff1', 'password_hash': hash_password('123456'),
        'full_name': 'Nhân viên Test', 'role': ROLE_STAFF, 'phone': '', 'active': True,
    })
    mongo.db.users.insert_one({
        'username': 'kitchen1', 'password_hash': hash_password('123456'),
        'full_name': 'Bếp Test', 'role': ROLE_KITCHEN, 'phone': '', 'active': True,
    })
    mongo.db.tables.insert_one({'name': 'Bàn 01', 'capacity': 4, 'status': 'trong'})
    cat_id = mongo.db.categories.insert_one({'name': 'Bia'}).inserted_id
    mongo.db.menu_items.insert_one({
        'name': 'Bia Saigon', 'category_id': cat_id, 'price': 15000,
        'unit': 'chai', 'recipe': [], 'available': True,
    })


def login(client, username, password='123456'):
    return client.post('/auth/login', data={'username': username, 'password': password},
                        follow_redirects=True)
