from bson import ObjectId
from datetime import datetime
from app.extensions import mongo


class Attendance:
    @staticmethod
    def get_open_shift(user_id):
        """Ca làm việc chưa check-out của nhân viên (nếu có)."""
        return mongo.db.attendance.find_one({
            'user_id': ObjectId(user_id),
            'check_out': None
        })

    @staticmethod
    def check_in(user_id):
        if Attendance.get_open_shift(user_id):
            raise ValueError('Bạn đang có một ca làm việc chưa check-out')
        doc = {
            'user_id': ObjectId(user_id),
            'check_in': datetime.utcnow(),
            'check_out': None,
            'hours': None,
        }
        return mongo.db.attendance.insert_one(doc).inserted_id

    @staticmethod
    def check_out(user_id):
        shift = Attendance.get_open_shift(user_id)
        if not shift:
            raise ValueError('Bạn chưa check-in ca làm việc nào')
        check_out_time = datetime.utcnow()
        hours = round((check_out_time - shift['check_in']).total_seconds() / 3600.0, 2)
        mongo.db.attendance.update_one(
            {'_id': shift['_id']},
            {'$set': {'check_out': check_out_time, 'hours': hours}}
        )
        return hours

    @staticmethod
    def get_history(user_id=None, date_from=None, date_to=None, limit=300):
        query = {}
        if user_id:
            query['user_id'] = ObjectId(user_id)
        if date_from or date_to:
            query['check_in'] = {}
            if date_from:
                query['check_in']['$gte'] = date_from
            if date_to:
                query['check_in']['$lte'] = date_to
        return list(mongo.db.attendance.find(query).sort('check_in', -1).limit(limit))

    @staticmethod
    def summarize_by_user(records):
        """Tổng hợp tổng số ca và tổng giờ làm theo từng nhân viên (dùng để tính lương)."""
        summary = {}
        for r in records:
            uid = str(r['user_id'])
            if uid not in summary:
                summary[uid] = {'shifts': 0, 'hours': 0.0}
            summary[uid]['shifts'] += 1
            summary[uid]['hours'] += r.get('hours') or 0
        return summary
