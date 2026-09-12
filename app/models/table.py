from bson import ObjectId
from app.extensions import mongo

STATUS_TRONG = 'trong'          # Bàn trống
STATUS_DANG_PHUC_VU = 'dang_phuc_vu'  # Đang có khách / đơn mở


class Table:
    @staticmethod
    def get_all():
        return list(mongo.db.tables.find().sort('name', 1))

    @staticmethod
    def find_by_id(table_id):
        return mongo.db.tables.find_one({'_id': ObjectId(table_id)})

    @staticmethod
    def create(name, capacity=4):
        doc = {'name': name, 'capacity': int(capacity), 'status': STATUS_TRONG}
        return mongo.db.tables.insert_one(doc).inserted_id

    @staticmethod
    def update(table_id, name=None, capacity=None):
        updates = {}
        if name is not None:
            updates['name'] = name
        if capacity is not None:
            updates['capacity'] = int(capacity)
        if updates:
            mongo.db.tables.update_one({'_id': ObjectId(table_id)}, {'$set': updates})

    @staticmethod
    def delete(table_id):
        mongo.db.tables.delete_one({'_id': ObjectId(table_id)})

    @staticmethod
    def set_status(table_id, status):
        mongo.db.tables.update_one({'_id': ObjectId(table_id)}, {'$set': {'status': status}})
