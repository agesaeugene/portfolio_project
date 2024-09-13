from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))

    # Link User to Log (One User can have multiple Logs)
    logs = db.relationship('Log', backref='user', lazy=True)

log_food = db.Table(
    'log_food', 
    db.Column('log_id', db.Integer, db.ForeignKey('log.id'), primary_key=True), 
    db.Column('food_id', db.Integer, db.ForeignKey('food.id'), primary_key=True),
    extend_existing=True
)

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    proteins = db.Column(db.Integer, nullable=False)
    carbs = db.Column(db.Integer, nullable=False)
    fats = db.Column(db.Integer, nullable=False)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    
    # Foreign key linking each log to a specific user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Many-to-many relationship between Log and Food
    foods = db.relationship('Food', secondary=log_food, backref='logs')
