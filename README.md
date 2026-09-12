# Hệ thống Quản lý Bán hàng Quán Bia

Ứng dụng web quản lý bán hàng cho quán bia, xây dựng bằng **Python Flask** (kiến trúc **MVC**) và **MongoDB**.

## 1. Tính năng chính

| Nghiệp vụ | Mô tả |
|---|---|
| Gọi món & phục vụ | Sơ đồ bàn, mở đơn, gọi món, theo dõi trạng thái món (đang chế biến / đã phục vụ), màn hình bếp/bar riêng |
| Thanh toán | Tính tiền theo đơn, áp giảm giá %, nhiều hình thức thanh toán (tiền mặt/chuyển khoản/quẹt thẻ), in hóa đơn |
| Quản lý kho | Danh mục nguyên liệu, nhập/xuất kho, cảnh báo tồn thấp, **tự động trừ kho theo công thức món khi bán** |
| Chấm công | Check-in/check-out theo ca, tự tính số giờ làm, tổng hợp theo nhân viên để làm cơ sở tính lương |
| Báo cáo | Doanh thu theo ngày, món bán chạy, doanh thu theo hình thức thanh toán, báo cáo tồn kho |
| Quản trị hệ thống | Phân quyền theo vai trò, quản lý danh mục/món, quản lý bàn, quản lý tài khoản nhân viên |

### Vai trò & phân quyền
- **admin** (Chủ quán/Quản trị): toàn quyền
- **manager** (Quản lý): toàn quyền trừ quản lý tài khoản nhân viên
- **cashier** (Thu ngân): gọi món, thanh toán
- **staff** (Nhân viên phục vụ): gọi món, xem bếp/bar
- **kitchen** (Bếp/Quầy bar): cập nhật trạng thái món

## 2. Kiến trúc MVC

```
quanbia/
├── run.py                     # Điểm khởi chạy ứng dụng
├── config.py                  # Cấu hình
├── seed_data.py                # Script tạo dữ liệu mẫu
├── requirements.txt
├── .env.example                # Mẫu file biến môi trường
└── app/
    ├── __init__.py             # App factory, đăng ký blueprint
    ├── extensions.py           # mongo, login_manager, hash tiện ích
    ├── models/                 # MODEL - thao tác với MongoDB
    │   ├── user.py
    │   ├── menu.py              (Category, MenuItem)
    │   ├── table.py
    │   ├── order.py
    │   ├── invoice.py
    │   ├── inventory.py         (InventoryItem, InventoryTransaction)
    │   └── attendance.py
    ├── controllers/             # CONTROLLER - Flask blueprint / route
    │   ├── auth_controller.py
    │   ├── main_controller.py
    │   ├── menu_controller.py
    │   ├── order_controller.py
    │   ├── table_controller.py
    │   ├── inventory_controller.py
    │   ├── attendance_controller.py
    │   ├── report_controller.py
    │   ├── user_controller.py
    │   └── decorators.py        # @roles_required
    ├── templates/                # VIEW - Jinja2 + Bootstrap 5
    └── static/                   # CSS/JS
```

## 3. Cài đặt

### Yêu cầu
- Python 3.10+
- MongoDB (chạy local hoặc MongoDB Atlas)

### Các bước

```bash
cd quanbia

# Tạo môi trường ảo (khuyến nghị)
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Cài thư viện
pip install -r requirements.txt

# Tạo file .env từ mẫu và chỉnh sửa nếu cần
cp .env.example .env
# Mở .env, cập nhật SECRET_KEY và MONGO_URI (mặc định: mongodb://localhost:27017/quanbia_db)

# Đảm bảo MongoDB đang chạy, ví dụ chạy local bằng Docker:
# docker run -d -p 27017:27017 --name mongo mongo:7

# Khởi tạo dữ liệu mẫu (tài khoản, danh mục, món, bàn, kho)
python seed_data.py

# Chạy ứng dụng
python run.py
```

Truy cập: http://localhost:5000

### Tài khoản mẫu (sau khi chạy `seed_data.py`)

| Tên đăng nhập | Mật khẩu | Vai trò |
|---|---|---|
| admin | admin123 | Chủ quán / Quản trị |
| quanly | quanly123 | Quản lý |
| thungan | thungan123 | Thu ngân |
| phucvu | phucvu123 | Nhân viên phục vụ |
| bepbar | bepbar123 | Bếp / Quầy bar |

> ⚠️ Đây là dữ liệu demo. Khi triển khai thật, hãy đổi mật khẩu và đặt `SECRET_KEY` mạnh trong `.env`.

## 4. Luồng sử dụng cơ bản

1. Đăng nhập bằng một trong các tài khoản mẫu ở trên.
2. Vào **Thực đơn** (vai trò admin/quản lý) để thêm danh mục, món ăn/đồ uống; có thể gắn "công thức" tiêu hao nguyên liệu để hệ thống tự trừ kho khi bán.
3. Vào **Kho hàng** để nhập nguyên liệu ban đầu (đá, bia, đồ nhắm...) và thiết lập ngưỡng cảnh báo.
4. Vào **Gọi món / Bàn**, chọn 1 bàn trống, mở đơn, thêm món.
5. Bên **Bếp / Bar**, nhân viên bếp bấm "Xong" khi món đã chế biến xong.
6. Thu ngân vào bàn đó, bấm **Thanh toán**, nhập giảm giá (nếu có) và chọn hình thức thanh toán → hệ thống tạo hóa đơn và tự động trừ kho.
7. Nhân viên **Chấm công**: check-in đầu ca, check-out cuối ca.
8. Quản lý xem **Báo cáo** doanh thu/tồn kho/chấm công theo khoảng thời gian.

## 5. Ghi chú kỹ thuật

- Mật khẩu được băm bằng `bcrypt`, không lưu plaintext.
- Xác thực & phiên đăng nhập dùng `Flask-Login`.
- Phân quyền theo route bằng decorator `@roles_required(...)` tùy biến (`app/controllers/decorators.py`).
- Toàn bộ giá tiền hiển thị qua Jinja filter `currency`, ngày giờ qua filter `datetime_vn` (định nghĩa trong `app/__init__.py`).
- Dữ liệu lưu trong các collection MongoDB: `users`, `categories`, `menu_items`, `tables`, `orders`, `invoices`, `inventory_items`, `inventory_transactions`, `attendance`.
- Đã kiểm thử luồng nghiệp vụ chính (đăng nhập, gọi món, thanh toán có trừ kho tự động, chấm công, phân quyền chặn truy cập trái phép) bằng smoke test nội bộ trước khi bàn giao.

## 6. Hướng phát triển tiếp theo (gợi ý, đúng như tài liệu dự án)

- Đặt bàn trực tuyến, gọi món bằng mã QR
- Tích hợp cổng thanh toán điện tử thực tế
- Quản lý nhiều chi nhánh
- Tính lương tự động dựa trên bảng chấm công
