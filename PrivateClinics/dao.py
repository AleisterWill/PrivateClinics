from datetime import datetime

from PrivateClinics import db, app
from PrivateClinics.models import User, Medicine, MedType, MedUnit, Schedule, Receipt, BillDetails
from flask_login import current_user
from sqlalchemy import func, and_, or_, desc
import hashlib


def get_users():
    return User.query.all()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_user_by_phone_number(phone_number):
    return User.query.filter(User.phone_number.__eq__(phone_number.strip())).first()


def load_med_type():
    return MedType.query.all()


def load_med_unit():
    return MedUnit.query.all()


def load_medicines():
    return Medicine.query.all()


def signup(first_name, last_name, sex, date_of_birth, address, phone_number, password, avatar):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    u = User(first_name=first_name, sex=sex, date_of_birth=date_of_birth, address=address, last_name=last_name,
             phone_number=phone_number, password=password, avatar=avatar)
    db.session.add(u)
    db.session.commit()


def auth_user(phone_number, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.phone_number.__eq__(phone_number.strip()),
                             User.password.__eq__(password)).first()


def add_schedule(user_id, date):
    s = Schedule(user_id=user_id, date=date)
    db.session.add(s)
    db.session.commit()


def count_schedules_by_date(date):
    return db.session.query(func.count(Schedule.id)) \
        .where(Schedule.date.__eq__(date)).first()


def schedule_details_by_date(date):
    query = db.session.query(Schedule.id, User.first_name + ' ' + User.last_name, User.sex, User.date_of_birth,
                             User.address) \
        .join(User, User.id.__eq__(Schedule.user_id), isouter=True) \
        .where(Schedule.date.__eq__(date))

    return query.all()


def get_schedule_by_id(schedule_id):
    return Schedule.query.get(schedule_id)


def lich_su_benh_by_user_id(user_id):
    query = db.session.query(Schedule, User) \
        .join(User, User.id.__eq__(Schedule.user_id), isouter=True) \
        .where(and_(User.id.__eq__(user_id)))

    return query.all()


def load_meds_by_type_name_ingredients(med_type_id, q, page, max_results):
    query = db.session.query(Medicine, MedUnit) \
        .join(MedUnit, MedUnit.id.__eq__(Medicine.med_unit_id))

    if med_type_id:
        query = query.filter(
            Medicine.med_type_id == med_type_id,
        )

    if q:
        query = query.filter(
            or_(Medicine.name.contains(q), Medicine.ingredients.contains(q))
        )

    return query.paginate(page=page, per_page=max_results)


def add_bill_details(medicine_id, quantity, usage, sch_id):
    bd = BillDetails(medicine_id=medicine_id, quantity=quantity, usage=usage, schedule_id=sch_id)
    db.session.add(bd)
    db.session.commit()


def update_schedule_by_id(schedule_id, symptoms, diagnosis):
    schedule = Schedule.query.get(schedule_id)
    if symptoms:
        schedule.symptoms = symptoms
    if diagnosis:
        schedule.diagnosis = diagnosis

    db.session.merge(schedule)
    db.session.commit()


def create_receipt_by_schedule_id(medicine_expense, schedule_id):
    schedule = Schedule.query.get(schedule_id)
    bill_details = BillDetails.query.filter(BillDetails.schedule_id.__eq__(schedule_id)).all()
    examination_fee = app.config['EXAMINATION_FEE']
    medicine_expense = medicine_expense,
    receipt = Receipt(
        examination_fee=examination_fee,
        medicine_expense=medicine_expense,
        total=examination_fee + medicine_expense,
        status='Payment Pending',
        schedule_id=schedule_id
    )
    db.session.add(receipt)
    db.session.commit()


def get_medicine_by_id(medicine_id):
    return Medicine.query.get(medicine_id)


def receipt_lookup(q=None, date=None):
    if not q:
        return None
    else:
        query = db.session.query(Receipt, Schedule) \
            .join(Schedule, Schedule.id.__eq__(Receipt.schedule_id), isouter=True) \
            .join(User, User.id.__eq__(Schedule.user_id))

        query = query.filter(
            User.phone_number.contains(q)
        )

        if date:
            query = query.filter(
                Schedule.date.__eq__(date)
            )

        return query.order_by(desc(Receipt.created_date)).all()


def confirm_payment(receipt_id):
    receipt = Receipt.query.get(receipt_id)

    receipt.status = 'Paid'
    receipt.payment_date = datetime.now()

    db.session.merge(receipt)
    db.session.commit()


def get_receipt_by_id(receipt_id):
    return Receipt.query.get(receipt_id)


def revenue_by_date(month_year=None):
    try:
        d = func.date(Receipt.payment_date)
        count = func.count(Receipt.id)
        sum = func.sum(Receipt.total)
        query = db.session.query(d, count, sum)

        query = query.filter(
            func.date_format(Receipt.payment_date, '%Y-%m').__eq__(month_year)
        )

        query = query.group_by(d)
        return query.all()
    except:
        pass
    return None


def med_usage_stas_by_date(month_year=None):
    try:
        sum = func.sum(BillDetails.quantity)
        count_distinct = func.count(func.distinct(BillDetails.schedule_id))

        query = db.session.query(Medicine.name, MedUnit.name, sum, count_distinct)\
                .join(Medicine, Medicine.med_unit_id == MedUnit.id)\
                .join(BillDetails, BillDetails.medicine_id == Medicine.id)\
                .join(Receipt, BillDetails.schedule_id == Receipt.schedule_id)\
                .where(func.date_format(Receipt.payment_date, '%Y-%m') == month_year)

        return query.group_by(Medicine.name).all()
    except:
        pass
    return None