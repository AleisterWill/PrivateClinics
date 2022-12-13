import cloudinary.uploader
from PrivateClinics import app, dao, admin, login, utils, controllers
from flask import render_template, request, redirect, session, jsonify

app.add_url_rule("/", 'home', controllers.home, methods=['get'])
app.add_url_rule("/accounts", 'accounts', controllers.accounts, methods=['get', 'post'])
app.add_url_rule("/signin", 'sign_in', controllers.sign_in, methods=['post'])
app.add_url_rule("/signout", 'sign_out', controllers.sign_out)
app.add_url_rule("/schedulev1", 'schedulev1', controllers.schedulev1, methods=['get', 'post'])
app.add_url_rule("/schedulev2", 'schedulev2', controllers.schedulev2, methods=['get', 'post'])
app.add_url_rule("/schedule", 'schedule', controllers.schedule)
app.add_url_rule("/lapphieukham", 'lapphieukham', controllers.lapphieukham, methods=['get', 'post'])
app.add_url_rule("/medlookup", 'medlookup', controllers.med_lookup)
app.add_url_rule("/receiptlookup", 'receipt_lookup', controllers.receipt_lookup)

app.add_url_rule("/api/cart", 'add_to_cart', controllers.add_to_cart, methods=['post'])
app.add_url_rule("/api/cart/uQ<int:id>", 'update_quantity', controllers.update_quantity, methods=['put'])
app.add_url_rule("/api/cart/uU<int:id>", 'update_usage', controllers.update_usage, methods=['put'])
app.add_url_rule("/api/cart/del<int:id>", 'del_cart_item', controllers.del_cart_item, methods=['delete'])
app.add_url_rule("/api/receipt/confirm/<int:id>", 'confirm_payment', controllers.confirm_payment, methods=['put'])


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.context_processor
def common_attr():
    med_types = dao.load_med_type()
    return {
        'med_types': med_types,
        'cart': utils.cart_stats(session.get(app.config['CART_KEY']))
    }


if __name__ == '__main__':
    app.run(debug=True)
