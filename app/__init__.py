from flask import Flask
from config import Config
from app.extensions import mongo, login_manager
from app.models.user import User


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.find_by_id(user_id)

    # Đăng ký các blueprint (controller)
    from app.controllers.auth_controller import auth_bp
    from app.controllers.main_controller import main_bp
    from app.controllers.menu_controller import menu_bp
    from app.controllers.order_controller import order_bp
    from app.controllers.table_controller import table_bp
    from app.controllers.inventory_controller import inventory_bp
    from app.controllers.attendance_controller import attendance_bp
    from app.controllers.report_controller import report_bp
    from app.controllers.user_controller import user_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(table_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(user_bp)

    register_template_utils(app)
    register_error_handlers(app)

    return app


def register_template_utils(app):
    @app.template_filter('currency')
    def currency_filter(value):
        try:
            return f"{value:,.0f} đ".replace(',', '.')
        except (TypeError, ValueError):
            return value

    @app.template_filter('datetime_vn')
    def datetime_vn_filter(value, fmt='%H:%M %d/%m/%Y'):
        if not value:
            return ''
        return value.strftime(fmt)

    @app.context_processor
    def inject_role_constants():
        from app.models.user import ROLE_ADMIN, ROLE_MANAGER, ROLE_CASHIER, ROLE_STAFF, ROLE_KITCHEN
        return dict(
            ROLE_ADMIN=ROLE_ADMIN, ROLE_MANAGER=ROLE_MANAGER, ROLE_CASHIER=ROLE_CASHIER,
            ROLE_STAFF=ROLE_STAFF, ROLE_KITCHEN=ROLE_KITCHEN,
        )


def register_error_handlers(app):
    from flask import render_template

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
