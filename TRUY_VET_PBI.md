# Truy vết Commit tới PBI

Do dự án được phát triển xong trước khi áp dụng Git, toàn bộ code được đưa vào
1 commit khởi tạo duy nhất: `b3521ab` (`feat(PBI-001): init du an...`).

Bảng dưới đây ánh xạ commit đó với từng PBI cụ thể, dựa trên các file mã nguồn
tương ứng, để đảm bảo tính truy vết theo yêu cầu Definition of Done (mục 3).

| PBI | Mô tả | File mã nguồn chính | Commit |
|---|---|---|---|
| PBI-001 | Gọi món theo bàn | `app/controllers/order_controller.py`, `app/models/order.py`, `app/models/table.py`, `app/templates/order/table_grid.html`, `table_detail.html` | b3521ab |
| PBI-002 | Bếp cập nhật trạng thái món | `app/controllers/order_controller.py` (route `/kitchen`, `/item/<idx>/status`), `app/templates/order/kitchen.html` | b3521ab |
| PBI-003 | Tính tiền, giảm giá | `app/controllers/order_controller.py` (route `checkout`), `app/models/invoice.py` | b3521ab |
| PBI-004 | In hóa đơn, hình thức thanh toán | `app/controllers/order_controller.py` (route `invoice_detail`), `app/templates/order/invoice.html` | b3521ab |
| PBI-005 | Nhập/xuất kho, công thức | `app/controllers/inventory_controller.py`, `app/models/inventory.py` | b3521ab |
| PBI-006 | Cảnh báo tồn kho thấp | `app/controllers/inventory_controller.py` (route `/`, `/history`) | b3521ab |
| PBI-007 | Check-in/check-out | `app/controllers/attendance_controller.py` (route `check-in`, `check-out`) | b3521ab |
| PBI-008 | Tổng hợp giờ công | `app/controllers/attendance_controller.py` (route `/all`) | b3521ab |
| PBI-009 | Báo cáo doanh thu | `app/controllers/report_controller.py` (route `/revenue`) | b3521ab |
| PBI-010 | Báo cáo tồn kho | `app/controllers/report_controller.py` (route `/inventory`) | b3521ab |
| PBI-011 | Phân quyền người dùng | `app/controllers/decorators.py`, `app/controllers/user_controller.py` | b3521ab |
| PBI-012 | Quản lý danh mục món/giá | `app/controllers/menu_controller.py` | b3521ab |

**Quy ước cho các thay đổi sau này:** mọi commit mới phát sinh từ việc sửa lỗi,
thêm tính năng đều phải ghi rõ mã PBI liên quan trong tên commit, theo mẫu:
`feat(PBI-XXX): mo ta thay doi` hoặc `fix(PBI-XXX): mo ta loi da sua`.
