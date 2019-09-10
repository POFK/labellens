#!/usr/bin/env python
# coding=utf-8
from app.response import Response
from flask import render_template, flash, redirect, url_for
from flask import jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask import request
from flask import send_from_directory
from werkzeug.urls import url_parse

from app import app
from app import db
from app.forms import LoginForm
from app.forms import RegistrationForm
from app.forms import ConfigurationForm

from app import models
User = models.User
Conf = models.Conf
Catalog = models.Catalog
Image = models.Image
Tag = models.Tag


ress = {}


@login_required
def res_init(user):
    ress[user.id] = ress.get(user.id, Response(user))
    ress[user.id].get_conf()
    return ress[user.id]


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html", title='Home Page')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        res = res_init(current_user)
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        res = res_init(current_user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    try:
        ress.pop(current_user.id)
    except:
        print(ress.keys())
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        ress[user.id] = Response(user)
        ress[user.id].set_default_conf()
        ress.pop(user.id)  # need remove it?
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    form = ConfigurationForm()
    if form.validate_on_submit():
        query = Conf.query.filter_by(user_id=current_user.id)
        assert query.count() < 2, \
            "There should be only one setting item per user!"
        data = {
            "grade_a": form.grade_a.data,
            "grade_b": form.grade_b.data,
            "grade_c": form.grade_c.data,
            "nonlens": form.nonlens.data,
            "next_im": form.next_im.data,
            "prev_im": form.prev_im.data,
        }

        if query.count() == 0:
            data["user"] = current_user
            conf = Conf(**data)
            db.session.add(conf)
        else:
            query.update(data)
        db.session.commit()
        res = res_init(current_user)
        delattr(res,"keys")
        res.get_conf()
        return redirect(url_for('index'))
    return render_template('conf.html', title='Setting', form=form)


# ============================================================

@app.route('/workspace/filter_<int:num>', methods=['GET', 'POST'])
@login_required
def tag_filter(num):
    res = res_init(current_user)
    if num == 0:
        mes = res.filter_tagN()
    elif num == 1:
        mes = res.filter_tagA()
    elif num == 2:
        mes = res.filter_tagB()
    elif num == 3:
        mes = res.filter_tagC()
    elif num == 4:
        mes = res.filter_untag()
    elif num == 100:
        mes = res.filter_all()
    return mes


@app.route('/workspace/progress', methods=['GET', 'POST'])
@login_required
def get_progress():
    mess = res_init(current_user).get_progress()
    return mess


@app.route('/workspace/download', methods=['GET', 'POST'])
@login_required
def download():
    print("download...")
    res = res_init(current_user)
    path = res.download()
    dir_path = path.split("/result")[0]
    filename = "result"+path.split("/result")[1]
    return send_from_directory(dir_path, filename=filename, as_attachment=True)


@app.route('/workspace/control_<string:key>', methods=['GET', 'POST'])
def get_im(key):
    res = res_init(current_user)
    next_page = False
    if key in res.keys:
        res.keys[key]()
        next_page = res.next_page
    res.get_current_image()
    im = Image.query.filter_by(id=res.im_id).first()
    try:
        label = im.tags[current_user].name
    except KeyError:
        label = "-"
    mess = {
        "path": im.name,
        "catalog": im.catalog.name,
        "id": im.id,
        "key": key,
        "label": label,
    }
    if next_page:
        mess["last"] = "1"
        return mess
    return mess


@app.route('/workspace', methods=['GET', 'POST'])
@login_required
def workspace():
    res = res_init(current_user)
    res.filter_untag()
    return render_template('workspace.html', title='Workspace')
