from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.inventory import InventoryItem, InventoryTransaction, TX_NHAP
from app.models.user import ROLE_ADMIN, ROLE_MANAGER
from app.controllers.decorators import roles_required

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')


@inventory_bp.route('/')
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def index():
    items = InventoryItem.get_all()
    low_stock_ids = {str(i['_id']) for i in InventoryItem.get_low_stock()}
    return render_template('inventory/index.html', items=items, low_stock_ids=low_stock_ids)


@inventory_bp.route('/add', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def add_item():
    name = request.form.get('name', '').strip()
    unit = request.form.get('unit', '').strip()
    quantity = request.form.get('quantity', 0)
    min_quantity = request.form.get('min_quantity', 5)
    if name and unit:
        InventoryItem.create(name, unit, quantity, min_quantity)
        flash('Đã thêm nguyên liệu mới.', 'success')
    return redirect(url_for('inventory.index'))


@inventory_bp.route('/<item_id>/edit', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def edit_item(item_id):
    name = request.form.get('name')
    unit = request.form.get('unit')
    min_quantity = request.form.get('min_quantity')
    InventoryItem.update(item_id, name=name, unit=unit, min_quantity=min_quantity)
    flash('Đã cập nhật nguyên liệu.', 'success')
    return redirect(url_for('inventory.index'))


@inventory_bp.route('/<item_id>/delete', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def delete_item(item_id):
    InventoryItem.delete(item_id)
    flash('Đã xóa nguyên liệu.', 'info')
    return redirect(url_for('inventory.index'))


@inventory_bp.route('/transaction', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def create_transaction():
    item_id = request.form.get('item_id')
    tx_type = request.form.get('type', TX_NHAP)
    qty = float(request.form.get('qty', 0) or 0)
    note = request.form.get('note', '')

    if qty <= 0:
        flash('Số lượng phải lớn hơn 0.', 'danger')
        return redirect(url_for('inventory.index'))

    try:
        InventoryTransaction.create(item_id, tx_type, qty, note, current_user.id)
        label = 'Nhập kho' if tx_type == TX_NHAP else 'Xuất kho'
        flash(f'{label} thành công.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')

    return redirect(url_for('inventory.index'))


@inventory_bp.route('/history')
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def history():
    transactions = InventoryTransaction.get_history()
    return render_template('inventory/history.html', transactions=transactions)
