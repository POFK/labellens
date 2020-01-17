#!/usr/bin/env python
# coding=utf-8
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import orm
from app import db
from app import login

attribute_mapped_collection = orm.collections.attribute_mapped_collection


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    conf = db.relationship('Conf', backref='user', lazy='dynamic')
    tags = db.relationship('Tag', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Conf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade_1 = db.Column(db.String(1))
    grade_2 = db.Column(db.String(1))
    grade_3 = db.Column(db.String(1))
    grade_4 = db.Column(db.String(1))
    grade_5 = db.Column(db.String(1))
    nonlens = db.Column(db.String(1))
    next_im = db.Column(db.String(1))
    prev_im = db.Column(db.String(1))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<key map {}>'.format(self.__dict__)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# --------------------- image label --------------------------


image_label = db.Table('tags',
                       db.Column('tag_id', db.Integer,
                                 db.ForeignKey('tag.id')),
                       db.Column('image_id', db.Integer,
                                 db.ForeignKey('image.id'))
                       )


class Catalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, unique=True)
    images = db.relationship('Image', backref='catalog', lazy='dynamic')

    def __repr__(self):
        return '<CAT {} path: {}>'.format(self.id, self.name)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    catalog_id = db.Column(db.Integer, db.ForeignKey('catalog.id'))
    tags = db.relationship('Tag', secondary=image_label,
                           collection_class=attribute_mapped_collection(
                               'tag_key'),
                           backref=db.backref('images', lazy='dynamic'))

    def __repr__(self):
        return '<Image {} {} @ Cat {}, Tag {}>'.format(self.id,
                                                       self.name,
                                                       self.catalog_id,
                                                       self.tags)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def tag_key(self):
        return self.user

    def __repr__(self):
        return '<Tag {} by {}>'.format(self.name, self.user)


def get_untagged_image(u):
    tag_u = Tag.query.filter(Tag.user == u)
    myfilter = [~Image.tags.contains(i) for i in tag_u]
    return Image.query.filter(*myfilter)
