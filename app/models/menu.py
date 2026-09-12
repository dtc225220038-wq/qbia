from bson import ObjectId
from datetime import datetime
from app.extensions import mongo


class Category:
    @staticmethod
    def get_all():
        return list(mongo.db.categories.find().sort('name', 1))

    @staticmethod
    def create(name):
        return mongo.db.categories.insert_one({'name': name}).inserted_id

    @staticmethod
    def update(cat_id, name):
        mongo.db.categories.update_one({'_id': ObjectId(cat_id)}, {'$set': {'name': name}})

    @staticmethod
    def delete(cat_id):
        mongo.db.categories.delete_one({'_id': ObjectId(cat_id)})

    @staticmethod
    def find_by_id(cat_id):
        return mongo.db.categories.find_one({'_id': ObjectId(cat_id)})


class MenuItem:
    """Món ăn / đồ uống trong thực đơn quán bia."""

    @staticmethod
    def get_all(available_only=False, category_id=None):
        query = {}
        if available_only:
            query['available'] = True
        if category_id:
            query['category_id'] = ObjectId(category_id)
        return list(mongo.db.menu_items.find(query).sort('name', 1))

    @staticmethod
    def find_by_id(item_id):
        return mongo.db.menu_items.find_one({'_id': ObjectId(item_id)})

    @staticmethod
    def create(name, category_id, price, unit='ly', recipe=None, available=True):
        """recipe: danh sách nguyên liệu tiêu hao mỗi khi bán 1 đơn vị món,
        dạng [{'inventory_id': ObjectId, 'qty': số lượng tiêu hao}]"""
        doc = {
            'name': name,
            'category_id': ObjectId(category_id) if category_id else None,
            'price': float(price),
            'unit': unit,
            'available': available,
            'recipe': recipe or [],
            'created_at': datetime.utcnow(),
        }
        return mongo.db.menu_items.insert_one(doc).inserted_id

    @staticmethod
    def update(item_id, name=None, category_id=None, price=None, unit=None,
               available=None, recipe=None):
        updates = {}
        if name is not None:
            updates['name'] = name
        if category_id is not None:
            updates['category_id'] = ObjectId(category_id) if category_id else None
        if price is not None:
            updates['price'] = float(price)
        if unit is not None:
            updates['unit'] = unit
        if available is not None:
            updates['available'] = available
        if recipe is not None:
            updates['recipe'] = recipe
        if updates:
            mongo.db.menu_items.update_one({'_id': ObjectId(item_id)}, {'$set': updates})

    @staticmethod
    def delete(item_id):
        mongo.db.menu_items.delete_one({'_id': ObjectId(item_id)})
