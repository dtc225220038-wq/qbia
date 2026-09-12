from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.table import Table, STATUS_TRONG
from app.models.order import Order, ITEM_DANG_CHE_BIEN, ITEM_DA_PHUC_VU
from app.models.menu import MenuItem, Category
from app.models.invoice import Invoice, PAYMENT_LABELS
from app.models.inventory import InventoryTransaction
from app.models.user import ROLE_ADMIN, ROLE_MANAGER, ROLE_CASHIER, ROLE_STAFF, ROLE_KITCHEN
from app.controllers.decorators import roles_required

order_bp = Blueprint('order', __name__, url_prefix='/orders')


@order_bp.route('/')
@login_required
def table_grid():
    tables = Table.get_all()
    # gắn kèm đơn đang mở (nếu có) để hiển thị tổng tiền tạm tính trên mỗi bàn
    for t in tables:
        order = Order.get_open_order_for_table(t['_id'])
        t['open_order'] = order
        t['subtotal'] = Order.calc_subtotal(order) if order else 0
    return render_template('order/table_grid.html', tables=tables)


@order_bp.route('/table/<table_id>')
@login_required
def view_table(table_id):
    table = Table.find_by_id(table_id)
    if not table:
        flash('Không tìm thấy bàn.', 'danger')
        return redirect(url_for('order.table_grid'))

    order = Order.get_open_order_for_table(table_id)
    categories = Category.get_all()
    menu_items = MenuItem.get_all(available_only=True)
    subtotal = Order.calc_subtotal(order) if order else 0
    return render_template('order/table_detail.html', table=table, order=order,
                            categories=categories, menu_items=menu_items, subtotal=subtotal)


@order_bp.route('/table/<table_id>/open', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER, ROLE_STAFF, ROLE_CASHIER)
def open_order(table_id):
    Order.create_order(table_id, current_user.id)
    return redirect(url_for('order.view_table', table_id=table_id))


@order_bp.route('/table/<table_id>/add_item', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER, ROLE_STAFF, ROLE_CASHIER)
def add_item(table_id):
    order_id_str = request.form.get('order_id')
    if not order_id_str:
        order_id_str = str(Order.create_order(table_id, current_user.id))

    item_id = request.form.get('item_id')
    qty = request.form.get('qty', 1)
    note = request.form.get('note', '')

    menu_item = MenuItem.find_by_id(item_id)
    if not menu_item:
        flash('Món không tồn tại.', 'danger')
    else:
        Order.add_item(order_id_str, menu_item, qty, note)
        flash(f'Đã thêm "{menu_item["name"]}" vào đơn.', 'success')

    return redirect(url_for('order.view_table', table_id=table_id))


@order_bp.route('/<order_id>/item/<int:idx>/status', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER, ROLE_STAFF, ROLE_KITCHEN)
def update_item_status(order_id, idx):
    status = request.form.get('status', ITEM_DA_PHUC_VU)
    Order.update_item_status(order_id, idx, status)
    next_url = request.form.get('next') or url_for('order.kitchen_queue')
    return redirect(next_url)


@order_bp.route('/<order_id>/item/<int:idx>/remove', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER, ROLE_STAFF)
def remove_item(order_id, idx):
    order = Order.find_by_id(order_id)
    Order.remove_item(order_id, idx)
    flash('Đã xóa món khỏi đơn.', 'info')
    return redirect(url_for('order.view_table', table_id=order['table_id']))


@order_bp.route('/kitchen')
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER, ROLE_KITCHEN, ROLE_STAFF)
def kitchen_queue():
    orders = Order.get_kitchen_queue()
    tables = {str(t['_id']): t for t in Table.get_all()}
    return render_template('order/kitchen.html', orders=orders, tables=tables,
                            ITEM_DANG_CHE_BIEN=ITEM_DANG_CHE_BIEN, ITEM_DA_PHUC_VU=ITEM_DA_PHUC_VU)


@order_bp.route('/<order_id>/checkout', methods=['GET', 'POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER, ROLE_CASHIER)
def checkout(order_id):
    order = Order.find_by_id(order_id)
    if not order:
        flash('Không tìm thấy đơn hàng.', 'danger')
        return redirect(url_for('order.table_grid'))

    subtotal = Order.calc_subtotal(order)

    if request.method == 'POST':
        discount = float(request.form.get('discount_percent', 0) or 0)
        payment_method = request.form.get('payment_method', 'cash')

        invoice_id = Invoice.create(order, discount, payment_method, current_user.id)

        # Trừ kho theo công thức của từng món đã bán
        for line in order['items']:
            menu_item = MenuItem.find_by_id(line['item_id'])
            if menu_item and menu_item.get('recipe'):
                for ing in menu_item['recipe']:
                    InventoryTransaction.deduct_for_sale(
                        ing['inventory_id'], ing['qty'] * line['qty'], order_id, current_user.id
                    )

        Order.mark_paid(order_id)
        Table.set_status(order['table_id'], STATUS_TRONG)
        flash('Thanh toán thành công!', 'success')
        return redirect(url_for('order.invoice_detail', invoice_id=invoice_id))

    return render_template('order/checkout.html', order=order, subtotal=subtotal,
                            payment_labels=PAYMENT_LABELS)


@order_bp.route('/invoice/<invoice_id>')
@login_required
def invoice_detail(invoice_id):
    invoice = Invoice.find_by_id(invoice_id)
    if not invoice:
        flash('Không tìm thấy hóa đơn.', 'danger')
        return redirect(url_for('order.table_grid'))
    return render_template('order/invoice.html', invoice=invoice,
                            payment_labels=PAYMENT_LABELS)


@order_bp.route('/<order_id>/cancel', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def cancel_order(order_id):
    order = Order.find_by_id(order_id)
    Order.cancel(order_id)
    flash('Đã hủy đơn hàng.', 'info')
    return redirect(url_for('order.table_grid'))
