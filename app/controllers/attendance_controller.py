from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.models.attendance import Attendance
from app.models.user import User, ROLE_ADMIN, ROLE_MANAGER
from app.controllers.decorators import roles_required

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')


@attendance_bp.route('/')
@login_required
def my_attendance():
    open_shift = Attendance.get_open_shift(current_user.id)
    history = Attendance.get_history(user_id=current_user.id, limit=30)
    return render_template('attendance/my_attendance.html', open_shift=open_shift, history=history)


@attendance_bp.route('/check-in', methods=['POST'])
@login_required
def check_in():
    try:
        Attendance.check_in(current_user.id)
        flash('Check-in thành công. Chúc bạn ca làm việc hiệu quả!', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('attendance.my_attendance'))


@attendance_bp.route('/check-out', methods=['POST'])
@login_required
def check_out():
    try:
        hours = Attendance.check_out(current_user.id)
        flash(f'Check-out thành công. Bạn đã làm việc {hours} giờ.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('attendance.my_attendance'))


@attendance_bp.route('/all')
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def all_attendance():
    date_from_str = request.args.get('from')
    date_to_str = request.args.get('to')
    date_from = datetime.strptime(date_from_str, '%Y-%m-%d') if date_from_str else None
    date_to = datetime.strptime(date_to_str, '%Y-%m-%d') if date_to_str else None

    records = Attendance.get_history(date_from=date_from, date_to=date_to, limit=1000)
    summary = Attendance.summarize_by_user(records)

    users = {u.id: u for u in User.get_all()}

    return render_template('attendance/all_attendance.html', records=records,
                            summary=summary, users=users,
                            date_from=date_from_str, date_to=date_to_str)
