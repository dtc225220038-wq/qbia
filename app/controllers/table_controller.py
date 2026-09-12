from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models.table import Table
from app.models.order import Order
from app.models.user import ROLE_ADMIN, ROLE_MANAGER
from app.controllers.decorators import roles_required

table_bp = Blueprint('table', __name__, url_prefix='/tables')


@table_bp.route('/manage')
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def manage():
    tables = Table.get_all()
    return render_template('order/table_manage.html', tables=tables)


@table_bp.route('/add', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def add():
    name = request.form.get('name', '').strip()
    capacity = request.form.get('capacity', 4)
    if name:
        Table.create(name, capacity)
        flash('Đã thêm bàn mới.', 'success')
    return redirect(url_for('table.manage'))


@table_bp.route('/<table_id>/delete', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def delete(table_id):
    if Order.get_open_order_for_table(table_id):
        flash('Không thể xóa bàn đang có đơn mở.', 'danger')
    else:
        Table.delete(table_id)
        flash('Đã xóa bàn.', 'info')
    return redirect(url_for('table.manage'))
