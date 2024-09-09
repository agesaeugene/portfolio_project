from flask import Blueprint, render_template
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/add')
def add():
    return render_template("add.html", user=current_user)

@views.route('/view')
def view():
    return render_template("view.html", user=current_user)