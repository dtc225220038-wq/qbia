from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models.menu import Category, MenuItem
from app.models.inventory import InventoryItem
from app.models.user import ROLE_ADMIN, ROLE_MANAGER
from app.controllers.decorators import roles_required

menu_bp = Blueprint('menu', __name__, url_prefix='/menu')


@menu_bp.route('/')
@login_required
def index():
    categories = Category.get_all()
    items = MenuItem.get_all()
    cat_map = {str(c['_id']): c['name'] for c in categories}
    return render_template('menu/index.html', categories=categories, items=items, cat_map=cat_map)


@menu_bp.route('/categories/add', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def add_category():
    name = request.form.get('name', '').strip()
    if name:
        Category.create(name)
        flash('Đã thêm danh mục.', 'success')
    return redirect(url_for('menu.index'))


@menu_bp.route('/categories/<cat_id>/delete', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def delete_category(cat_id):
    items_in_category = [i for i in MenuItem.get_all() if str(i.get('category_id')) == cat_id]
    if items_in_category:
        flash(f'Không thể xóa: còn {len(items_in_category)} món thuộc danh mục này. '
              f'Hãy xóa hoặc chuyển các món đó sang danh mục khác trước.', 'danger')
    else:
        Category.delete(cat_id)
        flash('Đã xóa danh mục.', 'info')
    return redirect(url_for('menu.index'))


@menu_bp.route('/items/add', methods=['GET', 'POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def add_item():
    categories = Category.get_all()
    inventory_items = InventoryItem.get_all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id') or None
        price = request.form.get('price', 0)
        unit = request.form.get('unit', 'ly')
        available = bool(request.form.get('available'))

        recipe = []
        ing_ids = request.form.getlist('recipe_item_id')
        ing_qtys = request.form.getlist('recipe_qty')
        for iid, qty in zip(ing_ids, ing_qtys):
            if iid and qty:
                recipe.append({'inventory_id': iid, 'qty': float(qty)})

        if not name or not price:
            flash('Vui lòng nhập đủ tên món và giá bán.', 'danger')
        else:
            MenuItem.create(name, category_id, price, unit, recipe, available)
            flash('Đã thêm món mới vào thực đơn.', 'success')
            return redirect(url_for('menu.index'))

    return render_template('menu/form.html', item=None, categories=categories,
                            inventory_items=inventory_items)


@menu_bp.route('/items/<item_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def edit_item(item_id):
    item = MenuItem.find_by_id(item_id)
    categories = Category.get_all()
    inventory_items = InventoryItem.get_all()
    if not item:
        flash('Không tìm thấy món.', 'danger')
        return redirect(url_for('menu.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id') or None
        price = request.form.get('price', 0)
        unit = request.form.get('unit', 'ly')
        available = bool(request.form.get('available'))

        recipe = []
        ing_ids = request.form.getlist('recipe_item_id')
        ing_qtys = request.form.getlist('recipe_qty')
        for iid, qty in zip(ing_ids, ing_qtys):
            if iid and qty:
                recipe.append({'inventory_id': iid, 'qty': float(qty)})

        MenuItem.update(item_id, name, category_id, price, unit, available, recipe)
        flash('Đã cập nhật món.', 'success')
        return redirect(url_for('menu.index'))

    return render_template('menu/form.html', item=item, categories=categories,
                            inventory_items=inventory_items)


@menu_bp.route('/items/<item_id>/delete', methods=['POST'])
@login_required
@roles_required(ROLE_ADMIN, ROLE_MANAGER)
def delete_item(item_id):
    MenuItem.delete(item_id)
    flash('Đã xóa món khỏi thực đơn.', 'info')
    return redirect(url_for('menu.index'))
