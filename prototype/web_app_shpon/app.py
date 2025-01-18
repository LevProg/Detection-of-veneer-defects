import threading
from flask import Flask, render_template, request, make_response, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import socket
import io
import os
from PIL import Image
import redis

matplotlib.use('Agg')
from io import BytesIO
import base64
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/shpon2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# with app.app_context():
#   app.config['Shpon_list'] = []
db = SQLAlchemy(app)
migrate = Migrate(app, db)
r = redis.StrictRedis(host='localhost', port=6379, db=0)
SHPON_QUEUE = 'shpon_queue'
SHPON_LIST_MUTEX = threading.Lock()
# SHPON_LIST = []
socketio = SocketIO(app)


class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, unique=True)
    post = db.Column(db.String)
    fio = db.Column(db.String)
    service_number = db.Column(db.Integer, unique=True)
    password = db.Column(db.String)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Shpon(db.Model):
    __tablename__ = 'shpon'
    shpon_id = db.Column(db.Integer, primary_key=True)
    defect = db.Column(db.Boolean)
    date_time = db.Column(db.DateTime, default=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    accuracy = db.Column(db.Boolean)


class Session_History(db.Model):
    __tablename__ = 'session__history'
    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    start_session = db.Column(db.DateTime, default=datetime.datetime.now)
    end_session = db.Column(db.DateTime)
    shpon_number = db.Column(db.Integer)


logging.basicConfig(level=logging.INFO)


@app.route("/", methods=("POST", "GET"))
@app.route("/login", methods=("POST", "GET"))
def login():
    if request.method == 'POST':
        return check_login_password(request.form['login'], request.form['password'])
    else:
        return render_template('login.html')


@app.route("/lk")
def lk():
    user = Users.query.filter(Users.user_id == 1).first()
    info = {
        'fio': user.fio,
        'post': user.post,
        'service_number': user.service_number
    }
    return render_template('lk.html', info=info)


@app.route("/analitics", methods=("POST", "GET"))
def analitics():
    path = 'C:/Users/burla/web_app_shpon/static/Analytics.png'
    if request.method == 'POST':
        start = request.get_json()['start']
        end = request.get_json()['end']
        num = request.get_json()['num']
        if num == 1:
            new_path = draw_graph1(start, end)
        elif num == 2:
            new_path = draw_graph2(start, end)
        elif num == 3:
            new_path = draw_graph3(start, end)
        return new_path
    return render_template('analitics.html', content=path)


@app.route("/index", methods=("POST", "GET"))
def index():
    # request.get_json()['defect'] дефекты: смотрим только если комманда=2, дефект=0 - нет дефекта, 1-5 номера дефектов
    # request.get_json()['id'] это будет айди шпона, ты его будешь изначально отдавать с фотками, а тут я буду возвращать айди выбранного шпона(который на главной)
    # тут нужно запускать и останавливать поток и менять в бдшке дефект, ещё желательно чтобы в бд было булевое поле чтобы понимать изменял ли оператор класс дефекта или нет
    add_new_image_to_web()
    if request.method == 'POST':
        if request.get_json()['command'] == 0:
            pass
        elif request.get_json()['command'] == 1:
            add_new_image_to_web()
        else:
            defect = request.get_json()['shpon_character']
            id = request.get_json()['shpon_id']
            change_defect(defect, id)
    img_data = r.lrange(SHPON_QUEUE, 0, -1)
    base64_images = []
    for data in img_data:
        base64_str = base64.b64encode(data).decode('utf-8')
        base64_images.append(base64_str)
    ides = r.lrange('shon_id', 0, -1)
    results = r.lrange('shon_result', 0, -1)

    return render_template('index.html', images=base64_images[:5], results=results, ides=ides)

    # return 'No images in queue', 404


def check_login_password(login, password):
    try:
        user = Users.query.filter_by(service_number=login).first()
        if user and user.check_password(password):
            new_session = Session_History(user_id=user.user_id, start_session=datetime.datetime.now())
            db.session.add(new_session)
            db.session.commit()
            return index()
        else:
            return "Invalid credentials", 401
    except Exception as e:
        logging.error(f"Error during login: {e}")
        return "An error occurred", 500


def draw_graph1(start_period, end_period):
    all = Shpon.query.filter(Shpon.date_time >= start_period, Shpon.date_time <= end_period)
    defect = all.filter(Shpon.defect == True).count()
    not_defect = all.filter(Shpon.defect == False).count()
    print(defect, not_defect)
    print('draw')
    data = [not_defect,defect]
    fig = plt.figure(figsize=(10, 7))
    plt.pie(data, labels=['Нет дефекта', 'Есть дефект'], autopct='%1.1f%%')
    plt.title(f'Распределение дефекта шпона с {start_period} по {end_period}')
    current_file = os.path.realpath(__file__)
    current_directory = os.path.dirname(current_file)
    filepath = current_directory + f'\\static\\graphics\\plot_{start_period}_{end_period}_1.png'
    print(filepath)
    plt.savefig(filepath)
    plt.close(fig)
    return F'static/graphics/plot_{start_period}_{end_period}_1.png'


def draw_graph2(start_period, end_period):
    # Creating dataset
    cars = ['Определено правильно', 'Ошибся']
    # ?можно взять модельку и сделать ещё распределение на классы
    all = Shpon.query.filter(Shpon.date_time >= start_period, Shpon.date_time <= end_period)
    accuracy = all.filter(Shpon.accuracy == True).count()
    not_accuracy = all.filter(Shpon.accuracy == False).count()
    data = [accuracy, 10]
    print(data)
    # Creating plot
    fig = plt.figure(figsize=(10, 7))
    plt.pie(data, labels=cars, autopct='%1.1f%%')
    plt.title(f'Погрешность определения ИИ дефекта у шпона с {start_period} по {end_period}')
    current_file = os.path.realpath(__file__)
    current_directory = os.path.dirname(current_file)
    filepath = current_directory + f'\\static\\graphics\\plot_{start_period}_{end_period}_2.png'
    print(filepath)
    plt.savefig(filepath)
    plt.close(fig)
    return F'static/graphics/plot_{start_period}_{end_period}_2.png'


def draw_graph3(start_period, end_period):
    return draw_graph1(start_period, end_period)


def change_defect(defect, id):
    user = db.session.get(Users, id)
    if user:
        user.defect = defect
        user.accuracy = False
        db.session.commit()


@socketio.on('connection')
def add_new_image_to_web():
    print("connect with socket")
    if not r.llen(SHPON_QUEUE) and not r.llen('shon_id') and not r.llen('shon_result'):
        image = r.lpop('SHPON_QUEUE')
        id = r.lpop('shon_id')
        res = r.lpop('shon_result')
        image = base64.b64encode(new_image_data).decode('utf-8')

        socketio.emit('new_image', {'image': image}, {'id': id}, {'res': res})


if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
