"""
Script khởi tạo dữ liệu mẫu cho hệ thống quản lý bán hàng Quán bia.
Chạy: python seed_data.py
"""
from app import create_app
from app.extensions import mongo
from app.models.user import User, ROLE_ADMIN, ROLE_MANAGER, ROLE_CASHIER, ROLE_STAFF, ROLE_KITCHEN
from app.models.menu import Category, MenuItem
from app.models.table import Table
from app.models.inventory import InventoryItem

app = create_app()

with app.app_context():
    print('Đang xóa dữ liệu cũ (nếu có)...')
    for col in ['users', 'categories', 'menu_items', 'tables', 'inventory_items',
                'inventory_transactions', 'orders', 'invoices', 'attendance']:
        mongo.db[col].delete_many({})

    print('Tạo tài khoản mẫu...')
    User.create('admin', 'admin123', 'Chủ quán (Admin)', ROLE_ADMIN)
    User.create('quanly', 'quanly123', 'Nguyễn Văn Quản Lý', ROLE_MANAGER)
    User.create('thungan', 'thungan123', 'Trần Thị Thu Ngân', ROLE_CASHIER)
    User.create('phucvu', 'phucvu123', 'Lê Văn Phục Vụ', ROLE_STAFF)
    User.create('bepbar', 'bepbar123', 'Phạm Thị Bếp Bar', ROLE_KITCHEN)

    print('Tạo danh mục & nguyên liệu kho...')
    cat_bia_id = Category.create('Bia')
    cat_nuoc_id = Category.create('Nước ngọt')
    cat_do_nhau_id = Category.create('Đồ nhắm')

    bia_tuoi_id = InventoryItem.create('Bia tươi', 'lít', 100, 10)
    bia_chai_id = InventoryItem.create('Bia chai Heineken', 'chai', 200, 20)
    nuoc_ngot_id = InventoryItem.create('Nước ngọt lon', 'lon', 100, 10)
    da_id = InventoryItem.create('Đá viên', 'kg', 50, 5)
    ca_muoi_id = InventoryItem.create('Cá khô', 'kg', 10, 2)
    dau_phong_id = InventoryItem.create('Đậu phộng', 'kg', 15, 2)

    print('Tạo món trong thực đơn...')
    MenuItem.create('Bia tươi', cat_bia_id, 15000, 'ly',
                     recipe=[{'inventory_id': str(bia_tuoi_id), 'qty': 0.5}])
    MenuItem.create('Bia chai Heineken', cat_bia_id, 25000, 'chai',
                     recipe=[{'inventory_id': str(bia_chai_id), 'qty': 1}])
    MenuItem.create('Nước ngọt lon', cat_nuoc_id, 15000, 'lon',
                     recipe=[{'inventory_id': str(nuoc_ngot_id), 'qty': 1}])
    MenuItem.create('Cá khô chiên nước mắm', cat_do_nhau_id, 90000, 'đĩa',
                     recipe=[{'inventory_id': str(ca_muoi_id), 'qty': 0.3}])
    MenuItem.create('Đậu phộng rang muối', cat_do_nhau_id, 40000, 'đĩa',
                     recipe=[{'inventory_id': str(dau_phong_id), 'qty': 0.2}])

    print('Tạo danh sách bàn...')
    for i in range(1, 11):
        Table.create(f'Bàn {i}', capacity=4 if i % 3 else 6)

    print('Hoàn tất! Tài khoản đăng nhập:')
    print('  admin    / admin123    (Chủ quán / Quản trị)')
    print('  quanly   / quanly123   (Quản lý)')
    print('  thungan  / thungan123  (Thu ngân)')
    print('  phucvu   / phucvu123   (Nhân viên phục vụ)')
    print('  bepbar   / bepbar123   (Bếp / Quầy bar)')
