from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, DateTime, Enum, Date
from sqlalchemy.orm import relationship
from PrivateClinics import app, db, dao
from datetime import datetime
from enum import Enum as UserEnum
from flask_login import UserMixin


class UserRole(UserEnum):
    ADMIN = 'ADMIN'
    DOCTOR = 'DOCTOR'
    NURSE = 'NURSE'
    EMPLOYEE = 'EMPLOYEE'
    PATIENT = 'PATIENT'


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class User(BaseModel, UserMixin):
    __tablename__ = 'user'

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    sex = Column(String(1))
    date_of_birth = Column(Date)
    address = Column(String(500))
    phone_number = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    active = Column(Boolean, default=True)
    user_role = Column(Enum(UserRole), default=UserRole.PATIENT)

    schedules = relationship('Schedule', backref='user', lazy=True)

    def __str__(self):
        return "{} {} - {}".format(self.first_name, self.last_name, self.phone_number)


class MedType(BaseModel):
    __tablename__ = 'med_type'

    name = Column(String(50), nullable=False)
    description = Column(String(500))

    medicines = relationship('Medicine', backref='med_type', lazy=True)

    def __str__(self):
        return self.name


class MedUnit(BaseModel):
    __tablename__ = 'med_unit'

    name = Column(String(10), nullable=False)

    medicines = relationship('Medicine', backref='med_unit', lazy=False)

    def __str__(self):
        return self.name


class Medicine(BaseModel):
    __tablename__ = 'medicine'

    name = Column(String(100), nullable=False)
    ingredients = Column(String(500))
    price_per_unit = Column(Float, default=0)
    image = Column(String(500))

    med_type_id = Column(Integer, ForeignKey(MedType.id), nullable=False)
    med_unit_id = Column(Integer, ForeignKey(MedUnit.id), nullable=False)

    bills_details = relationship('BillDetails', backref='medicine', lazy=True)

    def __str__(self):
        return self.name


class Schedule(BaseModel):
    __tablename__ = 'schedule'
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    date = Column(Date)
    symptoms = Column(String(500))
    diagnosis = Column(String(500))

    bills_details = relationship('BillDetails', backref='schedule', lazy=True)
    receipts = relationship('Receipt', backref='schedule', lazy=True)

    def __str__(self):
        return '{} - {}'.format(self.date.__str__(), dao.get_user_by_id(self.user_id))


class BillDetails(BaseModel):
    __tablename__ = 'bill_details'

    medicine_id = Column(Integer, ForeignKey(Medicine.id), nullable=True)
    quantity = Column(Integer, default=1)
    usage = Column(String(500))

    schedule_id = Column(Integer, ForeignKey(Schedule.id), nullable=False)


class Receipt(BaseModel):
    __tablename__ = 'receipt'

    examination_fee = Column(Float, default=0)
    medicine_expense = Column(Float)
    total = Column(Float)
    status = Column(String(50))
    created_date = Column(DateTime, default=datetime.now())
    payment_date = Column(DateTime)

    schedule_id = Column(Integer, ForeignKey(Schedule.id), nullable=False)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
