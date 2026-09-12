from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models.invoice import Invoice
from app.models.inventory import InventoryItem
from app.models.order import Order
from app.models.table import Table, STATUS_DANG_PHUC_VU
from app.models.attendance import Attendance

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def dashboard():
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    invoices_today = Invoice.get_by_date_range(today_start, today_end)
    revenue_today = sum(i['total'] for i in invoices_today)

    low_stock = InventoryItem.get_low_stock()
    open_orders = Order.get_open_orders()
    tables = Table.get_all()
    tables_busy = len([t for t in tables if t.get('status') == STATUS_DANG_PHUC_VU])

    my_open_shift = None
    if current_user.is_authenticated:
        my_open_shift = Attendance.get_open_shift(current_user.id)

    return render_template(
        'dashboard.html',
        revenue_today=revenue_today,
        invoices_count=len(invoices_today),
        low_stock=low_stock,
        open_orders=open_orders,
        tables_total=len(tables),
        tables_busy=tables_busy,
        my_open_shift=my_open_shift,
    )
