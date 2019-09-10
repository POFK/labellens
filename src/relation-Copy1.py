#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from flask_sqlalchemy import orm
from flask_migrate import Migrate
import os
from datetime import datetime

attribute_mapped_collection = orm.collections.attribute_mapped_collection

basedir = "/home/mtx/git/ranklens/app/test"


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or         'sqlite:///' + os.path.join(basedir, 'test_many2many.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# In[2]:


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    tags = db.relationship('Tag', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return '<User {}>'.format(self.username)


# In[3]:


tags = db.Table('tags',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                db.Column('page_id', db.Integer, db.ForeignKey('page.id'))
                )


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    tags = db.relationship('Tag', secondary=tags,
                           collection_class=attribute_mapped_collection(
                                 'tag_key'),
                           backref=db.backref('pages', lazy='dynamic'))

    def __repr__(self):
        #return '<Page {} Tag {}>'.format(self.name, self.tags.all())
        return '<Page {} Tag {}>'.format(self.name, self.tags)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    @property
    def tag_key(self):
        return self.user

    def __repr__(self):
        return '<Tag {} : {}>'.format(self.name, self.user)


# In[4]:


def get_untagged_image(u):    
    tag_u = Tag.query.filter(Tag.user==u)
    myfilter=[~Page.tags.contains(i) for i in tag_u]
    return Page.query.filter(*myfilter).all()


# In[5]:


db.drop_all()


# In[6]:


db.create_all()


# ## create users, pages and tags

# In[7]:


u = User(username='test', email='test@test.com')
u2 = User(username='test2', email='test2@test.com')
db.session.add(u)
db.session.add(u2)
db.session.commit()


# In[8]:


User.query.all()


# In[9]:


t1 = Tag(name='A', user=u)
t2 = Tag(name='B', user=u)
t3 = Tag(name='C', user=u)
t4 = Tag(name='A', user=u2)
t5 = Tag(name='B', user=u2)
t6 = Tag(name='C', user=u2)
db.session.add_all([t1,t2,t3,t4,t5,t6])
db.session.commit()


# In[10]:


p1 = Page(name='p1')
p2 = Page(name='p2')
db.session.add_all([p1,p2])
db.session.commit()


# In[11]:


Tag.query.all()


# In[12]:


Page.query.all()


# ## add tag on pages

# In[13]:


p1.tags[t1.user]=t1
p1.tags[t2.user]=t2
p2.tags[t2.user]=t2
p2.tags[t4.user]=t4


# In[14]:


Page.query.all()


# ## query test

# In[15]:


Page.query.join(Page.tags).filter(Tag.name=="A").all()


# In[16]:


Page.query.join(Page.tags).filter(Tag.name=="A").first().tags[u]


# In[17]:


db.session.query(tags).all()


# ### select un-tagged page under one user

# In[18]:


Page.query.all()


# In[19]:


get_untagged_image(u2)


# In[20]:


get_untagged_image(u)


# In[18]:


s1 = Tag.query.filter(Tag.user==u2)
fr=[~Page.tags.contains(i) for i in s1]
Page.query.filter(*fr).all()


# In[19]:


s1 = Tag.query.filter(Tag.user==u)
fr=[~Page.tags.contains(i) for i in s1]
Page.query.filter(*fr).all()


# ### select tag A pages under user 1

# In[21]:


Page.query.join(Page.tags).filter(Tag.name=="B").filter(Tag.user==u).all()


# In[22]:


Page.query.join(Page.tags).filter(Tag.name=="A").filter(Tag.user==u2).all()


# In[23]:


Page.query.join(Page.tags).filter(Tag.name=="B").filter(Tag.user==u2).all()


# In[24]:


t = Tag.query.filter(Tag.user_id==u.id).filter(Tag.name=='B').first()
t.pages.all()


# In[25]:


t = Tag.query.filter(Tag.user_id==u2.id).filter(Tag.name=='A').first()
t.pages.all()


# In[26]:


t = Tag.query.filter(Tag.user_id==u2.id).filter(Tag.name=='B').first()
t.pages.all()


# In[ ]:




