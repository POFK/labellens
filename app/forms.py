#!/usr/bin/env python
# coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ConfigurationForm(FlaskForm):
    grade_a = StringField("grade A:", default='1', validators=[DataRequired()])
    grade_b = StringField("grade B:", default='2', validators=[DataRequired()])
    grade_c = StringField("grade C:", default='3', validators=[DataRequired()])
    nonlens = StringField("nonlens:", default='0', validators=[DataRequired()])
    next_im = StringField("next image:", default='j',
                          validators=[DataRequired()])
    prev_im = StringField("previous image:", default='k',
                          validators=[DataRequired()])
    submit = SubmitField('Sure')


class FilterSelect(FlaskForm):
    myfilter = SelectField(
        label='Filter',
        choices=[(0, 'unlabelled'),
                 (1, 'grade A'),
                 (2, 'grade B'),
                 (3, 'grade C'),
                 (4, 'lens'),
                 (5, 'not lens'),
                 ],
        default=0,
        coerce=int,
    )
    submit = SubmitField('Sure')
