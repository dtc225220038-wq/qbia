from bson import ObjectId
from datetime import datetime
from app.extensions import mongo

PAYMENT_CASH = 'cash'            # Tiền mặt
PAYMENT_TRANSFER = 'transfer'    # Chuyển khoản
PAYMENT_CARD = 'card'            # Quẹt thẻ

PAYMENT_LABELS = {
    PAYMENT_CASH: 'Tiền mặt',
    PAYMENT_TRANSFER: 'Chuyển khoản',
    PAYMENT_CARD: 'Quẹt thẻ',
}


class Invoice:
    @staticmethod
    def create(order, discount_percent, payment_method, cashier_id):
        subtotal = sum(i['price'] * i['qty'] for i in order['items'])
        discount_amount = round(subtotal * (discount_percent / 100.0), 0)
        total = subtotal - discount_amount
        doc = {
            'order_id': order['_id'],
            'table_id': order['table_id'],
            'items': order['items'],
            'subtotal': subtotal,
            'discount_percent': discount_percent,
            'discount_amount': discount_amount,
            'total': total,
            'payment_method': payment_method,
            'cashier_id': ObjectId(cashier_id) if cashier_id else None,
            'paid_at': datetime.utcnow(),
        }
        return mongo.db.invoices.insert_one(doc).inserted_id

    @staticmethod
    def get_by_date_range(date_from, date_to):
        query = {}
        if date_from or date_to:
            query['paid_at'] = {}
            if date_from:
                query['paid_at']['$gte'] = date_from
            if date_to:
                query['paid_at']['$lte'] = date_to
        return list(mongo.db.invoices.find(query).sort('paid_at', -1))

    @staticmethod
    def find_by_id(invoice_id):
        return mongo.db.invoices.find_one({'_id': ObjectId(invoice_id)})
