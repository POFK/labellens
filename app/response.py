#!/usr/bin/env python
# coding=utf-8

import os
import glob
import numpy as np
import json
from datetime import datetime
from flask import request, render_template, redirect, url_for, flash
from flask_login import current_user

# ========================================
from app import db, app
from app import models
User = models.User
Conf = models.Conf
Catalog = models.Catalog
Image = models.Image
Tag = models.Tag
get_untagged_image = models.get_untagged_image
# ========================================


class Response(object):

    def __init__(self, user):
        self.u = user
        self.filter_all()
        self.base_dir = app.static_folder

    def set_default_conf(self):
        data = {
            "grade_a": "1",
            "grade_b": "2",
            "grade_c": "3",
            "nonlens": "0",
            "next_im": "j",
            "prev_im": "k",
        }
        data["user"] = self.u
        conf = Conf(**data)
        db.session.add(conf)
        db.session.commit()

    def get_conf(self):
        try:
            self.keys
        except AttributeError:
            conf = Conf.query.filter_by(user_id=self.u.id).one()
            self.conf = dict(conf.__dict__)
            self._conf_method()

    def _conf_method(self):
        if Tag.query.filter_by(user_id=self.u.id).count() == 0:
            tags = []
            for tag in ["A", "B", "C", "N"]:
                tags.append(Tag(name=tag, user=self.u))
            db.session.add_all(tags)
            db.session.commit()
        self.keys = {}
        self.keys[self.conf['grade_a']] = self.method(label="A", act=None)
        self.keys[self.conf['grade_b']] = self.method(label="B", act=None)
        self.keys[self.conf['grade_c']] = self.method(label="C", act=None)
        self.keys[self.conf['nonlens']] = self.method(label="N", act=None)
        self.keys[self.conf['next_im']] = self.method(
            label=None, act=self.next)
        self.keys[self.conf['prev_im']] = self.method(
            label=None, act=self.prev)

    def get_current_image(self):
        try:
            self.im_id
        except AttributeError:
            self.im_id = self.im_query.first().id

    def method(self, label=None, act=None):
        def func():
            if label is not None:
                self.add_tag(label)
                self.next()
            if act is not None:
                act()
        return func

    def next(self):
        self.get_current_image()
        im = Image.query.filter_by(id=self.im_id).first()
        if im.query.join(Image.tags).filter(Tag.user == self.u, Image.id == im.id).count() == 0:
            self.add_tag("N")
        next_image = self.im_query.order_by(
            Image.id.asc()).filter(Image.id > self.im_id).first()
        if next_image is None:
            self.next_page = True
        else:
            self.im_id = next_image.id
            self.next_page = False

    def prev(self):
        prev_image = self.im_query.order_by(
            Image.id.desc()).filter(Image.id < self.im_id).first()
        self.next_page = False
        if prev_image is None:
            prev_image = self.im_query.order_by(
                Image.id.desc()).first()
        self.im_id = prev_image.id

    def add_tag(self, l=''):
        l_tag = Tag.query.filter_by(user_id=self.u.id, name=l).first()
        self.get_current_image()
        im = Image.query.filter_by(id=self.im_id).first()
        im.tags[l_tag.user] = l_tag
        db.session.commit()

    def save(self):
        db.session.commit()

    def _auto_save(self):
        self.save()

    def filter_untag(self):
        self.__delattr__("im_query")
        self.im_query = get_untagged_image(self.u)
        try:
            self.im_id = self.im_query.order_by(Image.id.asc()).first().id
            return {}
        except AttributeError:
            self.filter_all()
            mess = "There is no unlabeled image, and all images are displayed."
            return {"message": mess}

    def filter_tagA(self):
        self.__delattr__("im_query")
        self.im_query = Image.query.join(Image.tags).filter(
            Tag.name == "A").filter(Tag.user == self.u)
        try:
            self.im_id = self.im_query.order_by(Image.id.asc()).first().id
            return {}
        except AttributeError:
            mess = "There is no grade-A level image, and all images are displayed."
            self.filter_all()
            return {"message": mess}

    def filter_tagB(self):
        self.__delattr__("im_query")
        self.im_query = Image.query.join(Image.tags).filter(
            Tag.name == "B").filter(Tag.user == self.u)
        try:
            self.im_id = self.im_query.order_by(Image.id.asc()).first().id
            return {}
        except AttributeError:
            mess = "There is no grade-B level image, and all images are displayed."
            self.filter_all()
            return {"message": mess}

    def filter_tagC(self):
        self.__delattr__("im_query")
        self.im_query = Image.query.join(Image.tags).filter(
            Tag.name == "C").filter(Tag.user == self.u)
        try:
            self.im_id = self.im_query.order_by(Image.id.asc()).first().id
            return {}
        except AttributeError:
            mess = "There is no grade-C level image, and all images are displayed."
            self.filter_all()
            return {"message": mess}

    def filter_tagN(self):
        self.__delattr__("im_query")
        self.im_query = Image.query.join(Image.tags).filter(
            Tag.name == "N").filter(Tag.user == self.u)
        try:
            self.im_id = self.im_query.order_by(Image.id.asc()).first().id
            return {}
        except AttributeError:
            mess = "There is no non-lensing image, and all images are displayed."
            self.filter_all()
            return {"message": mess}

    def filter_all(self):
        try:
            self.__delattr__("im_query")
        except AttributeError:
            pass
        self.im_query = Image.query
        self.im_id = self.im_query.order_by(Image.id.asc()).first().id
        return {}

    def get_progress(self):
        num_all = Image.query.count()
        num_tag = Image.query.join(Image.tags).filter(
            Tag.user == self.u).count()
        frac = int((num_tag/num_all) * 100)
        print(self.u.username, frac)
        return {"frac": "{:d}".format(frac)}

    def download(self):
        ims = Image.query.order_by(Image.id.asc()).all()
        text = []
        text.append("#author: {}\n".format(self.u.username))
        dt = datetime.now()
        text.append("#date: {}\n".format(dt.strftime("%c")))
        text.append("#column: image id, dir, image name, label\n")
        for im in ims:
            try:
                label = im.tags[self.u].name
            except KeyError:
                label = "-"
            prop = [im.id, im.catalog.name, im.name, label]
            t = "{},{},{},{}\n".format(*prop)
            text.append(t)
        path = os.path.join(self.base_dir, "result/"+self.u.username+'.txt')
        with open(path, 'w') as fp:
            fp.writelines(text)
        return path


class Data(object):
    """
    locd_cpt: load all file paths
    init_dataset: add file path to db, init db before using, if admit...
    user_label: define label per user
    load_conf: load configuration
    ::control::
        next: order_by, image_id > current im_id, first
        prev: order_by, image_id < current im_id, first
        add_tag: im[u] = label, if none, default nonlense
        save: db.commit()
        auto_save: ...
        filter: unlabeled, A, B, C, N...
    """

    def __init__(self, *args, **kwargs):
        super(Data, self).__init__(*args, **kwargs)
        self.base_dir = app.static_folder
        self.dirs = ["data", ]

    def init_dataset(self):
        """admin needed"""
        self.init_catalog()
        self.init_images()

    def init_catalog(self):
        """admin needed"""
        CAT = []
        for dir_path in self.dirs:
            cat = Catalog(name=dir_path)
            CAT.append(cat)
        db.session.add_all(CAT)
        db.session.commit()

    def init_images(self):
        """admin needed"""
        for dir_path in self.dirs:
            fps = self.get_fps(os.path.join(self.base_dir,dir_path))
            cat = Catalog.query.filter_by(name=dir_path).first()
            IMs = []
            for fp in fps:
                IMs.append(Image(name=fp, catalog=cat))
            db.session.add_all(IMs)
        db.session.commit()

    def get_fps(self, dir):
        files = glob.glob(os.path.join(dir, '*.png'))
        fps = [i.replace(dir + '/', '') for i in files]
        fps = np.sort(fps)
        return fps


if __name__ == '__main__':
    #   db.create_all()
    data = Data()
    data.init_dataset()
    u = User(username='admit', email="admit@test.com")
    res = Response(u)
