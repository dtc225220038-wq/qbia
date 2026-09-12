from flask_login import UserMixin
from bson import ObjectId
from bson.errors import InvalidId
from app.extensions import mongo, hash_password, check_password

# Các vai trò (role) trong hệ thống
ROLE_ADMIN = 'admin'          # Chủ quán / quản trị hệ thống
ROLE_MANAGER = 'manager'      # Quản lý
ROLE_CASHIER = 'cashier'      # Thu ngân
ROLE_STAFF = 'staff'          # Nhân viên phục vụ
ROLE_KITCHEN = 'kitchen'      # Bếp / quầy bar

ALL_ROLES = [ROLE_ADMIN, ROLE_MANAGER, ROLE_CASHIER, ROLE_STAFF, ROLE_KITCHEN]

ROLE_LABELS = {
    ROLE_ADMIN: 'Chủ quán / Quản trị',
    ROLE_MANAGER: 'Quản lý',
    ROLE_CASHIER: 'Thu ngân',
    ROLE_STAFF: 'Nhân viên phục vụ',
    ROLE_KITCHEN: 'Bếp / Quầy bar',
}


class User(UserMixin):
    """Model User bọc quanh collection 'users' của MongoDB."""

    def __init__(self, data):
        self.data = data

    # --- Thuộc tính bắt buộc cho Flask-Login ---
    def get_id(self):
        return str(self.data['_id'])

    @property
    def id(self):
        return str(self.data['_id'])

    @property
    def username(self):
        return self.data.get('username')

    @property
    def full_name(self):
        return self.data.get('full_name')

    @property
    def role(self):
        return self.data.get('role')

    @property
    def role_label(self):
        return ROLE_LABELS.get(self.role, self.role)

    @property
    def is_active_account(self):
        return self.data.get('active', True)

    @property
    def is_active(self):
        # Ghi đè thuộc tính is_active của Flask-Login: user bị khóa sẽ không đăng nhập được
        return self.data.get('active', True)

    def to_public_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'role_label': self.role_label,
            'active': self.is_active_account,
        }

    # --- Các hàm truy vấn ---
    @staticmethod
    def find_by_id(user_id):
        try:
            oid = ObjectId(user_id)
        except (InvalidId, TypeError):
            return None
        data = mongo.db.users.find_one({'_id': oid})
        return User(data) if data else None

    @staticmethod
    def find_by_username(username):
        data = mongo.db.users.find_one({'username': username})
        return User(data) if data else None

    @staticmethod
    def get_all(role=None):
        query = {}
        if role:
            query['role'] = role
        cursor = mongo.db.users.find(query).sort('full_name', 1)
        return [User(d) for d in cursor]

    @staticmethod
    def create(username, password, full_name, role, phone=''):
        if User.find_by_username(username):
            raise ValueError('Tên đăng nhập đã tồn tại')
        doc = {
            'username': username,
            'password_hash': hash_password(password),
            'full_name': full_name,
            'role': role,
            'phone': phone,
            'active': True,
        }
        result = mongo.db.users.insert_one(doc)
        return User.find_by_id(result.inserted_id)

    @staticmethod
    def update(user_id, full_name=None, role=None, phone=None, active=None):
        updates = {}
        if full_name is not None:
            updates['full_name'] = full_name
        if role is not None:
            updates['role'] = role
        if phone is not None:
            updates['phone'] = phone
        if active is not None:
            updates['active'] = active
        if updates:
            mongo.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': updates})

    @staticmethod
    def reset_password(user_id, new_password):
        mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'password_hash': hash_password(new_password)}}
        )

    def verify_password(self, password):
        return check_password(password, self.data.get('password_hash', ''))
