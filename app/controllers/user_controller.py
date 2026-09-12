from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models.user import User, ALL_ROLES, ROLE_LABELS, ROLE_ADMIN
from app.controllers.decorators import roles_required

user_bp = Blueprint('user', __name__, url_prefix='/users')


@user_bp.route('/')
@login_required
@roles_required(ROLE_ADMIN)
def index():
    users = User.get_all()
    return render_template('user/index.html', users=users, roles=ALL_ROLES, role_labels=ROLE_LABELS)


@user_bp.route('/add', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN)
def add():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    full_name = request.form.get('full_name', '').strip()
    role = request.form.get('role')
    phone = request.form.get('phone', '')

    if not (username and password and full_name and role):
        flash('Vui lòng nhập đầy đủ thông tin.', 'danger')
        return redirect(url_for('user.index'))

    try:
        User.create(username, password, full_name, role, phone)
        flash('Đã tạo tài khoản nhân viên mới.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')

    return redirect(url_for('user.index'))


@user_bp.route('/<user_id>/edit', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN)
def edit(user_id):
    full_name = request.form.get('full_name')
    role = request.form.get('role')
    phone = request.form.get('phone')
    active = request.form.get('active') == 'on'
    User.update(user_id, full_name=full_name, role=role, phone=phone, active=active)
    flash('Đã cập nhật thông tin nhân viên.', 'success')
    return redirect(url_for('user.index'))


@user_bp.route('/<user_id>/reset-password', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN)
def reset_password(user_id):
    new_password = request.form.get('new_password', '')
    if len(new_password) < 4:
        flash('Mật khẩu mới quá ngắn.', 'danger')
    else:
        User.reset_password(user_id, new_password)
        flash('Đã đặt lại mật khẩu.', 'success')
    return redirect(url_for('user.index'))
