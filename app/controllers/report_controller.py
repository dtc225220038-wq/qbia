from flask import Blueprint, render_template, request
from flask_login import login_required
from datetime import datetime, timedelta
from collections import defaultdict
from app.models.invoice import Invoice
from app.models.inventory import InventoryItem, InventoryTransaction
from app.models.user import ROLE_ADMIN, ROLE_MANAGER
from app.controllers.decorators import roles_required

report_bp = Blueprint('report', __name__, url_prefix='/reports')


def _parse_date_range():
    date_from_str = request.args.get('from')
    date_to_str = request.args.get('to')
    if date_from_str:
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
    else:
        date_from = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=6)
    if date_to_str:
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d') + timedelta(days=1)
    else:
        date_to = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return date_from, date_to, date_from_str, date_to_str


@report_bp.route('/revenue')
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def revenue():
    date_from, date_to, from_str, to_str = _parse_date_range()
    invoices = Invoice.get_by_date_range(date_from, date_to)

    total_revenue = sum(i['total'] for i in invoices)
    total_discount = sum(i['discount_amount'] for i in invoices)
    total_invoices = len(invoices)

    # Doanh thu theo ngày
    daily = defaultdict(float)
    for inv in invoices:
        day_key = inv['paid_at'].strftime('%d/%m/%Y')
        daily[day_key] += inv['total']
    daily_sorted = sorted(daily.items(), key=lambda x: datetime.strptime(x[0], '%d/%m/%Y'))

    # Món bán chạy
    item_sales = defaultdict(lambda: {'qty': 0, 'revenue': 0.0})
    for inv in invoices:
        for line in inv['items']:
            item_sales[line['name']]['qty'] += line['qty']
            item_sales[line['name']]['revenue'] += line['price'] * line['qty']
    top_items = sorted(item_sales.items(), key=lambda x: x[1]['revenue'], reverse=True)[:10]

    # Doanh thu theo hình thức thanh toán
    by_payment = defaultdict(float)
    for inv in invoices:
        by_payment[inv['payment_method']] += inv['total']

    return render_template(
        'report/revenue.html',
        invoices=invoices, total_revenue=total_revenue, total_discount=total_discount,
        total_invoices=total_invoices, daily_sorted=daily_sorted, top_items=top_items,
        by_payment=by_payment, date_from=from_str, date_to=to_str,
    )


@report_bp.route('/inventory')
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def inventory_report():
    items = InventoryItem.get_all()
    low_stock = InventoryItem.get_low_stock()

    date_from, date_to, from_str, to_str = _parse_date_range()
    transactions = InventoryTransaction.get_history(date_from, date_to)

    nhap_total = sum(t['qty'] for t in transactions if t['type'] == 'nhap')
    xuat_total = sum(t['qty'] for t in transactions if t['type'] == 'xuat')

    return render_template(
        'report/inventory.html', items=items, low_stock=low_stock,
        transactions=transactions, nhap_total=nhap_total, xuat_total=xuat_total,
        date_from=from_str, date_to=to_str,
    )
