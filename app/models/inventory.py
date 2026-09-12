from bson import ObjectId
from datetime import datetime
from app.extensions import mongo

TX_NHAP = 'nhap'   # Nhập kho
TX_XUAT = 'xuat'   # Xuất kho (bán hàng hoặc hao hụt)


class InventoryItem:
    """Nguyên liệu / hàng hóa trong kho (bia, đá, nước ngọt, đồ nhắm...)."""

    @staticmethod
    def get_all():
        return list(mongo.db.inventory_items.find().sort('name', 1))

    @staticmethod
    def find_by_id(item_id):
        return mongo.db.inventory_items.find_one({'_id': ObjectId(item_id)})

    @staticmethod
    def create(name, unit, quantity=0, min_quantity=5):
        doc = {
            'name': name,
            'unit': unit,
            'quantity': float(quantity),
            'min_quantity': float(min_quantity),
        }
        return mongo.db.inventory_items.insert_one(doc).inserted_id

    @staticmethod
    def update(item_id, name=None, unit=None, min_quantity=None):
        updates = {}
        if name is not None:
            updates['name'] = name
        if unit is not None:
            updates['unit'] = unit
        if min_quantity is not None:
            updates['min_quantity'] = float(min_quantity)
        if updates:
            mongo.db.inventory_items.update_one({'_id': ObjectId(item_id)}, {'$set': updates})

    @staticmethod
    def delete(item_id):
        mongo.db.inventory_items.delete_one({'_id': ObjectId(item_id)})

    @staticmethod
    def adjust_quantity(item_id, delta):
        """delta dương = nhập thêm, delta âm = xuất bớt."""
        mongo.db.inventory_items.update_one(
            {'_id': ObjectId(item_id)},
            {'$inc': {'quantity': delta}}
        )

    @staticmethod
    def get_low_stock():
        items = InventoryItem.get_all()
        return [i for i in items if i['quantity'] <= i.get('min_quantity', 0)]


class InventoryTransaction:
    @staticmethod
    def create(item_id, tx_type, qty, note, user_id):
        item = InventoryItem.find_by_id(item_id)
        if not item:
            raise ValueError('Nguyên liệu không tồn tại')

        delta = qty if tx_type == TX_NHAP else -qty
        InventoryItem.adjust_quantity(item_id, delta)

        doc = {
            'item_id': ObjectId(item_id),
            'item_name': item['name'],
            'type': tx_type,
            'qty': float(qty),
            'note': note,
            'user_id': ObjectId(user_id) if user_id else None,
            'created_at': datetime.utcnow(),
        }
        return mongo.db.inventory_transactions.insert_one(doc).inserted_id

    @staticmethod
    def deduct_for_sale(item_id, qty, order_id, user_id=None):
        """Tự động xuất kho theo định mức khi món được bán (dùng cho công thức món)."""
        item = InventoryItem.find_by_id(item_id)
        if not item:
            return
        InventoryItem.adjust_quantity(item_id, -qty)
        mongo.db.inventory_transactions.insert_one({
            'item_id': ObjectId(item_id),
            'item_name': item['name'],
            'type': TX_XUAT,
            'qty': float(qty),
            'note': f'Xuất tự động theo đơn hàng {order_id}',
            'user_id': ObjectId(user_id) if user_id else None,
            'created_at': datetime.utcnow(),
        })

    @staticmethod
    def get_history(date_from=None, date_to=None, limit=300):
        query = {}
        if date_from or date_to:
            query['created_at'] = {}
            if date_from:
                query['created_at']['$gte'] = date_from
            if date_to:
                query['created_at']['$lte'] = date_to
        return list(mongo.db.inventory_transactions.find(query).sort('created_at', -1).limit(limit))
