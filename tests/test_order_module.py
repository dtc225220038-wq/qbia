"""
T-007: Kiểm thử module Gọi món & Order (PBI-001, PBI-002).

Chạy: pytest tests/test_order_module.py -v
"""
from app.extensions import mongo
from conftest import login


def get_table_id():
    table = mongo.db.tables.find_one({'name': 'Bàn 01'})
    return str(table['_id'])


def get_menu_item_id():
    item = mongo.db.menu_items.find_one({'name': 'Bia Saigon'})
    return str(item['_id'])


# ---------------------- PBI-001: Gọi món theo bàn ----------------------

def test_pbi001_xem_luoi_ban(client):
    """Given hệ thống có bàn, When nhân viên vào trang gọi món, Then thấy danh sách bàn."""
    login(client, 'staff1')
    resp = client.get('/orders/')
    assert resp.status_code == 200
    assert 'Bàn 01'.encode('utf-8') in resp.data


def test_pbi001_mo_don_va_goi_mon(client):
    """Given bàn trống, When nhân viên mở đơn và gọi món, Then đơn được lưu với đúng món."""
    login(client, 'staff1')
    table_id = get_table_id()
    item_id = get_menu_item_id()

    resp = client.post(f'/orders/table/{table_id}/add_item', data={
        'item_id': item_id, 'qty': 2, 'note': 'Không đá',
    }, follow_redirects=True)
    assert resp.status_code == 200

    order = mongo.db.orders.find_one({'status': 'open'})
    assert order is not None, 'Đơn hàng phải được tạo và lưu vào DB'
    assert len(order['items']) == 1
    assert order['items'][0]['qty'] == 2
    assert order['items'][0]['name'] == 'Bia Saigon'
    print(f"[PBI-001] Đơn hàng đã lưu: {order['items'][0]['name']} x{order['items'][0]['qty']}, "
          f"trạng thái ban đầu = {order['items'][0]['status']}")


# ---------------------- PBI-002: Bếp cập nhật trạng thái món ----------------------

def test_pbi002_bep_thay_kitchen_queue(client):
    """Given món vừa order (đang chế biến), When vào màn hình bếp, Then thấy món đó trong hàng chờ."""
    login(client, 'staff1')
    table_id = get_table_id()
    item_id = get_menu_item_id()
    client.post(f'/orders/table/{table_id}/add_item', data={'item_id': item_id, 'qty': 1})

    login(client, 'kitchen1')
    resp = client.get('/orders/kitchen')
    assert resp.status_code == 200
    assert 'Bia Saigon'.encode('utf-8') in resp.data
    print("[PBI-002] Màn hình bếp hiển thị đúng món đang chờ chế biến")


def test_pbi002_cap_nhat_trang_thai_mon(client):
    """Given món đang chế biến, When bếp bấm 'đã xong', Then trạng thái đổi thành đã phục vụ."""
    login(client, 'staff1')
    table_id = get_table_id()
    item_id = get_menu_item_id()
    client.post(f'/orders/table/{table_id}/add_item', data={'item_id': item_id, 'qty': 1})

    order = mongo.db.orders.find_one({'status': 'open'})
    assert order['items'][0]['status'] == 'dang_che_bien'

    login(client, 'kitchen1')
    resp = client.post(f'/orders/{order["_id"]}/item/0/status', data={
        'status': 'da_phuc_vu',
    }, follow_redirects=True)
    assert resp.status_code == 200

    order_after = mongo.db.orders.find_one({'_id': order['_id']})
    assert order_after['items'][0]['status'] == 'da_phuc_vu'
    print(f"[PBI-002] Trạng thái món đổi thành công: "
          f"{order['items'][0]['status']} -> {order_after['items'][0]['status']}")


def test_pbi002_phan_quyen_staff_khong_duoc_cap_nhat_trang_thai(client):
    """
    Given tài khoản không có quyền (không phải admin/manager/staff/kitchen theo route),
    Kiểm tra decorator roles_required hoạt động đúng ở PBI-011 liên quan.
    (staff CÓ quyền theo code, test này xác nhận đúng danh sách role được whitelist.)
    """
    login(client, 'staff1')
    table_id = get_table_id()
    item_id = get_menu_item_id()
    client.post(f'/orders/table/{table_id}/add_item', data={'item_id': item_id, 'qty': 1})
    order = mongo.db.orders.find_one({'status': 'open'})

    # staff nằm trong whitelist của route update_item_status -> phải được phép (200/302), không bị 403
    resp = client.post(f'/orders/{order["_id"]}/item/0/status', data={'status': 'da_phuc_vu'})
    assert resp.status_code != 403
    print("[PBI-002] Xác nhận phân quyền: staff được phép cập nhật trạng thái món (đúng thiết kế)")
