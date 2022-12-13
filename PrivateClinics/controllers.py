import cloudinary.uploader
from PrivateClinics import app, dao, admin, login, utils, send_sms
from flask import render_template, request, redirect, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from PrivateClinics.decorators import anonymous_user, doctor_user, nurse_user, employee_user
from datetime import datetime


def home():
    return render_template("index.html")


@anonymous_user
def accounts():
    err_msg = ''
    if request.method == 'POST':
        password = request.form['passReg']
        confirm_pw = request.form['confirmPW']

        if password.__eq__(confirm_pw):
            avatar = ''
            if request.files:
                resp = cloudinary.uploader.upload(request.files['avatar'])
                avatar = resp['secure_url']

            try:
                dao.signup(
                    first_name=request.form['firstName'],
                    last_name=request.form['lastName'],
                    sex=request.form['sex'],
                    date_of_birth=request.form['dob'],
                    address=request.form['address'],
                    phone_number=request.form['phoneReg'],
                    password=request.form['passReg'],
                    avatar=avatar
                )

                return redirect("/accounts")
            except:
                err_msg = 'Đã có lỗi xảy ra! Vui lòng quay lại sau'
        else:
            err_msg = 'Xác nhận mật khẩu KHÔNG khớp'

    return render_template("accounts.html", err_msg=err_msg)


def sign_in():
    if request.method == 'POST':
        phone_number = request.form['phoneNum']
        password = request.form['password']

        user = dao.auth_user(phone_number=phone_number, password=password)
        if user:
            login_user(user=user)

    n = request.args.get('next')
    return redirect(n if n else '/')


def sign_out():
    logout_user()
    return redirect('/accounts')


@anonymous_user
def schedulev1():
    errmsg = ''
    successmsg = ''
    if request.method == 'POST':
        u = dao.get_user_by_phone_number(request.form['phone'])
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        sex = request.form['sex']
        date_of_birth = request.form['dob']
        address = request.form['address']
        phone_number = request.form['phone']
        date = request.form['date']

        if dao.count_schedules_by_date(date)[0] < app.config['MAX_PATIENTS_PER_DAY']:
            if not u:
                try:
                    dao.signup(
                        first_name=first_name,
                        last_name=last_name,
                        sex=sex,
                        date_of_birth=date_of_birth,
                        address=address,
                        phone_number=phone_number,
                        password='123456',
                        avatar=''
                    )
                except:
                    errmsg = 'Đã có lỗi xảy ra, vui lòng thử lại sau!'

                try:
                    dao.add_schedule(
                        user_id=dao.get_user_by_phone_number(request.form['phone']).id,
                        date=date
                    )
                    send_sms.send(
                        body='Bạn vừa đăng ký lịch hẹn khám vào {}.\n'
                             'Có thể đăng nhập vào website để theo dõi lịch khám bằng số điện thoại đã đăng ký với mật khẩu mặc định là 123456'.format(
                            date),
                        to='+84' + phone_number[1:-1]
                    )
                    successmsg = 'Đăng ký thành công. SMS thông tin sẽ được gửi đến số điện thoại đăng ký sau ít phút'
                except:
                    errmsg = 'Đã có lỗi xảy ra, vui lòng thử lại sau!'

            else:
                errmsg = 'Số điện thoại này đã được đăng ký, phải đăng nhập mới có thể thực hiện chức năng này.'

        else:
            errmsg = 'Số lượng đăng ký khám vượt hơn mức quy định trong ngày. Vui lòng chọn ngày khám khác!'

    return render_template("schedule.html", errmsg=errmsg, successmsg=successmsg)


@login_required
def schedulev2():
    errmsg = ''
    successmsg = ''
    if request.method == 'POST':
        date = request.form['date']
        if dao.count_schedules_by_date(date)[0] >= app.config['MAX_PATIENTS_PER_DAY']:
            errmsg = 'Số lượng đăng ký khám vượt hơn mức quy định trong ngày. Vui lòng chọn ngày khám khác!'
        else:
            try:
                dao.add_schedule(
                    user_id=current_user.id,
                    date=date
                )
                send_sms.send(
                    body='Bạn vừa đăng ký lịch hẹn khám vào {}'.format(date),
                    to='+84' + current_user.phone_number[1:-1]
                )
                successmsg = 'Đăng ký thành công. SMS thông tin sẽ được gửi đến số điện thoại đăng ký sau ít phút'
            except:
                errmsg = 'Đã có lỗi xảy ra, vui lòng thử lại sau!'

        # t1 = dao.count_schedules_by_date(date)
        # print(app.config['MAX_PATIENTS_PER_DAY'])
        # print(t1[0] > app.config['MAX_PATIENTS_PER_DAY'])

    return render_template("schedule.html", errmsg=errmsg, successmsg=successmsg)


def schedule():
    date = request.args.get("q")
    schedule_list = dao.schedule_details_by_date(date=date)

    print(schedule_list)

    return render_template("schedulelist.html", schedule_list=schedule_list, q=date)


@doctor_user
def lapphieukham():
    errmsg = ''
    successmsg = ''

    if request.method == 'POST':
        sch_id = request.form['sch_id']
        symptoms = request.form['symptoms']
        diagnosis = request.form['diagnosis']

        key = app.config['CART_KEY']
        cart = session[key]

        medicine_expense = 0
        try:
            for v in cart.values():
                dao.add_bill_details(medicine_id=v['id'], quantity=v['quantity'], usage=v['usage'], sch_id=sch_id)
                medicine_expense += dao.get_medicine_by_id(v['id']).price_per_unit * v['quantity']
            dao.update_schedule_by_id(schedule_id=sch_id, symptoms=symptoms, diagnosis=diagnosis)
            dao.create_receipt_by_schedule_id(medicine_expense=medicine_expense, schedule_id=sch_id)
            del cart
            successmsg = 'Phiếu khám bệnh đã được lập và thêm hóa đơn chờ thanh toán'
        except:
            errmsg = 'Đã có lỗi xảy ra, vui lòng thử lại sau'

    phone_number = request.args.get('q')
    diag = ''
    if phone_number:
        uid = dao.get_user_by_phone_number(phone_number).id
        # print(uid)
        diag = dao.lich_su_benh_by_user_id(uid)
        # print(diag)

    users = dao.get_users()

    return render_template("lapphieukham.html", users=users, diag=diag, errmsg=errmsg, successmsg=successmsg)


@doctor_user
def med_lookup():
    med_type_id = request.args.get('mtype', '')
    q = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    max_results = int(request.args.get('max_results', 8))

    med_list = dao.load_meds_by_type_name_ingredients(med_type_id, q, page, max_results)

    return render_template("medlist.html", med_list=med_list , page=page, max_results=max_results, q=q, mtype=med_type_id)


@doctor_user
def add_to_cart():
    data = request.json

    key = app.config['CART_KEY']
    cart = session[key] if key in session else {}

    id = str(data['id'])
    name = data['name']
    unit = data['unit']

    if id in cart:
        cart[id]['quantity'] += 1
    else:
        cart[id] = {
            "id": id,
            "name": name,
            "unit": unit,
            "quantity": 1,
            "usage": ''
        }

    session[key] = cart

    return jsonify(utils.cart_stats(cart))


@doctor_user
def update_quantity(id):
    key = app.config['CART_KEY']
    cart = session[key]

    if str(id) in cart:
        quantity = int(request.json['quantity'])
        cart[str(id)]['quantity'] = quantity

    session[key] = cart

    return jsonify(utils.cart_stats(cart))


@doctor_user
def update_usage(id):
    key = app.config['CART_KEY']
    cart = session[key]

    if str(id) in cart:
        usage = str(request.json['usage'])
        print(usage)
        cart[str(id)]['usage'] = usage

    session[key] = cart

    return jsonify(cart)


@doctor_user
def del_cart_item(id):
    key = app.config['CART_KEY']
    cart = session[key]

    if str(id) in cart:
        del cart[str(id)]

    session[key] = cart

    return jsonify(utils.cart_stats(cart))


@employee_user
def receipt_lookup():
    q = request.args.get("q")
    d = request.args.get("d")

    receipt_list = None
    user = None
    try:
        receipt_list = dao.receipt_lookup(q=q, date=d)
        user = dao.get_user_by_phone_number(q)
    except:
        pass

    return render_template("receiptlookup.html", receipt_list=receipt_list, user=user)


@employee_user
def confirm_payment(id):

    dao.confirm_payment(receipt_id=id)
    receipt = dao.get_receipt_by_id(receipt_id=id)
    return jsonify({
        "status": receipt.status,
        "payment_date": receipt.payment_date.__str__()
    })


