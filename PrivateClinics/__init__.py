from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babelex import Babel
import cloudinary

app = Flask(__name__)
app.secret_key = 'if93mda18497xzkd'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@localhost/privateclinics?charset=utf8mb4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['CART_KEY'] = 'cart'
app.config['MAX_PATIENTS_PER_DAY'] = 40
app.config['EXAMINATION_FEE'] = 100000
app.config['CART_KEY'] = 'cart'

db = SQLAlchemy(app=app)

login = LoginManager(app=app)

babel = Babel(app=app)

cloudinary.config(cloud_name='aleisterw', api_key='829342486126452', api_secret='Rtou-UwwUqPTqjrMJSTlCKZ1Lsw')


@babel.localeselector
def load_locate():
    return 'vi'
