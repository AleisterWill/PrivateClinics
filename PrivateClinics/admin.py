from PrivateClinics import db, app, dao
from PrivateClinics.models import User, Medicine, MedType, MedUnit, UserRole, Schedule, Receipt, BillDetails
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from sqlalchemy import func
from flask import request, redirect
from wtforms import TextAreaField
from wtforms.widgets import TextArea


class AuthenticatedAdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class AuthenticatedAdminView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class MedsView(AuthenticatedAdminModelView):
    column_searchable_list = ['name', 'ingredients']
    column_filters = ['name', 'price_per_unit']
    can_view_details = True
    page_size = 6


class MedTypeView(AuthenticatedAdminModelView):
    column_searchable_list = ['name']


class MedUnitView(AuthenticatedAdminModelView):
    column_searchable_list = ['name']


class MyAdminView(AdminIndexView):
    @expose('/', methods=['get', 'post'])
    def index(self):
        successmsg = ''
        if request.method == 'POST':
            if request.form['MAX_PATIENTS_PER_DAY']:
                app.config['MAX_PATIENTS_PER_DAY'] = int(request.form['MAX_PATIENTS_PER_DAY'])
            if request.form['EXAMINATION_FEE']:
                app.config['EXAMINATION_FEE'] = int(request.form['EXAMINATION_FEE'])
            successmsg = 'Lưu thay đổi thành công'

        mP = app.config['MAX_PATIENTS_PER_DAY']
        eF = app.config['EXAMINATION_FEE']

        return self.render('admin/index.html', mP=mP, eF=eF, successmsg=successmsg)


class StatisticView(AuthenticatedAdminView):
    @expose('/')
    def index(self):
        mY = request.args.get('mY')
        revenueStats = dao.revenue_by_date(
            month_year=mY
        )

        total = 0
        for r in revenueStats:
            total += r[2]

        medicineStats = dao.med_usage_stas_by_date(month_year=mY)
        return self.render('admin/stats.html', revenueStats=revenueStats, total=total, mY=mY, medicineStats=medicineStats)


admin = Admin(app=app, name='Quản trị Phòng mạch tư', template_mode='bootstrap4', index_view=MyAdminView())
admin.add_view(MedsView(Medicine, db.session, 'Thuốc'))
admin.add_view(MedTypeView(MedType, db.session, 'Loại thuốc'))
admin.add_view(MedUnitView(MedUnit, db.session, 'Đơn vị thuốc'))
admin.add_view(StatisticView(name='Thống kê - Báo cáo'))

