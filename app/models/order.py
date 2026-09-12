from bson import ObjectId
from datetime import datetime
from app.extensions import mongo
from app.models.table import Table, STATUS_TRONG, STATUS_DANG_PHUC_VU

ORDER_OPEN = 'open'          # Đơn đang mở (chưa thanh toán)
ORDER_PAID = 'paid'          # Đã thanh toán
ORDER_CANCELED = 'canceled'  # Đã hủy

ITEM_DANG_CHE_BIEN = 'dang_che_bien'
ITEM_DA_PHUC_VU = 'da_phuc_vu'

ITEM_STATUS_LABELS = {
    ITEM_DANG_CHE_BIEN: 'Đang chế biến',
    ITEM_DA_PHUC_VU: 'Đã phục vụ',
}


class Order:
    @staticmethod
    def get_open_order_for_table(table_id):
        return mongo.db.orders.find_one({'table_id': ObjectId(table_id), 'status': ORDER_OPEN})

    @staticmethod
    def find_by_id(order_id):
        return mongo.db.orders.find_one({'_id': ObjectId(order_id)})

    @staticmethod
    def get_open_orders():
        return list(mongo.db.orders.find({'status': ORDER_OPEN}).sort('created_at', 1))

    @staticmethod
    def get_kitchen_queue():
        """Các món đang chế biến trên mọi đơn mở, phục vụ cho màn hình bếp/bar."""
        return list(mongo.db.orders.find(
            {'status': ORDER_OPEN, 'items.status': ITEM_DANG_CHE_BIEN}
        ).sort('created_at', 1))

    @staticmethod
    def get_history(date_from=None, date_to=None, status=None, limit=200):
        query = {}
        if status:
            query['status'] = status
        if date_from or date_to:
            query['created_at'] = {}
            if date_from:
                query['created_at']['$gte'] = date_from
            if date_to:
                query['created_at']['$lte'] = date_to
        return list(mongo.db.orders.find(query).sort('created_at', -1).limit(limit))

    @staticmethod
    def create_order(table_id, created_by):
        existing = Order.get_open_order_for_table(table_id)
        if existing:
            return existing['_id']
        doc = {
            'table_id': ObjectId(table_id),
            'status': ORDER_OPEN,
            'items': [],
            'created_at': datetime.utcnow(),
            'created_by': ObjectId(created_by) if created_by else None,
            'closed_at': None,
        }
        order_id = mongo.db.orders.insert_one(doc).inserted_id
        Table.set_status(table_id, STATUS_DANG_PHUC_VU)
        return order_id

    @staticmethod
    def add_item(order_id, menu_item, qty, note=''):
        item_doc = {
            'item_id': menu_item['_id'],
            'name': menu_item['name'],
            'price': menu_item['price'],
            'qty': int(qty),
            'note': note,
            'status': ITEM_DANG_CHE_BIEN,
            'added_at': datetime.utcnow(),
        }
        mongo.db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {'$push': {'items': item_doc}}
        )

    @staticmethod
    def update_item_status(order_id, item_index, status):
        mongo.db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {f'items.{item_index}.status': status}}
        )

    @staticmethod
    def remove_item(order_id, item_index):
        order = Order.find_by_id(order_id)
        if not order:
            return
        items = order['items']
        if 0 <= item_index < len(items):
            items.pop(item_index)
            mongo.db.orders.update_one({'_id': ObjectId(order_id)}, {'$set': {'items': items}})

    @staticmethod
    def calc_subtotal(order):
        return sum(i['price'] * i['qty'] for i in order.get('items', []))

    @staticmethod
    def mark_paid(order_id):
        mongo.db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {'status': ORDER_PAID, 'closed_at': datetime.utcnow()}}
        )

    @staticmethod
    def cancel(order_id):
        order = Order.find_by_id(order_id)
        mongo.db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {'status': ORDER_CANCELED, 'closed_at': datetime.utcnow()}}
        )
        if order:
            Table.set_status(order['table_id'], STATUS_TRONG)
