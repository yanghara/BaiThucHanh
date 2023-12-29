from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from app.Models import Category, Product, UserRoleEnum
from app import app, db, dao
from flask_login import logout_user, current_user
from flask import redirect


class MyAdmin(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', stats=dao.count_productReceipt())


admin = Admin(app=app, name='QUẢN TRỊ BÁN HÀNG', template_mode='bootstrap4', index_view=MyAdmin())


class AuthenticatedAdmin(ModelView):  # ghi đè model view
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.ADMIN


class MyProductView(AuthenticatedAdmin):  # đang ghi đề lớp AuthenticatedAdmin
    column_list = ['id', 'name', 'price']
    can_export = True
    column_searchable_list = ['name', 'price']
    column_filters = ['name', 'price']
    column_editable_list = ['name', 'price']
    edit_modal = True


class MyCategory(AuthenticatedAdmin):
    column_list = ['name', 'products']

class AuthenticatedUser(BaseView):  # ghi đè base  view
    def is_accessible(self):
        return current_user.is_authenticated


class MyStatsView(AuthenticatedUser):
    @expose('/')
    def index(self):
        return self.render('admin/stas.html')


class MyLoginView(AuthenticatedUser):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


admin.add_view(MyCategory(Category, db.session))
admin.add_view(MyProductView(Product, db.session))
admin.add_view(MyStatsView(name='Thông tin báo cáo'))
admin.add_view(MyLoginView(name='Đăng xuất'))
