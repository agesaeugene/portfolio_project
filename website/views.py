from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from website.models import Food, Log
from .extensions import db
from sqlalchemy.exc import IntegrityError  
from datetime import datetime

views = Blueprint('views', __name__)

@views.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    
    return render_template("land.html")

@views.route('/home')
@login_required
def home():
    logs = Log.query.filter_by(user_id=current_user.id).order_by(Log.date.desc()).all()

    log_dates = []
        
    for log in logs:
        proteins = 0
        carbs = 0
        fat = 0
        calories = 0
        
        for food in log.foods:
            proteins += food.proteins
            carbs += food.carbs
            fat += food.fats
            calories += food.calories
            
        log_dates.append({
            'log': log,
            'log_date': log.date,
            'proteins': proteins,
            'carbs': carbs,
            'fat': fat,
            'calories': calories
        })

    return render_template("home.html", log_dates=log_dates, user=current_user)


@views.route('/create_log', methods=['POST'])
@login_required
def create_log():
    date = request.form.get('date')

    # Check if the date is empty
    if not date:
        flash('Please select a date!', 'error')
        return redirect(url_for('views.add_date'))  # Redirect back to the form

    try:
        # Attempt to parse the date
        log = Log(date=datetime.strptime(date, '%Y-%m-%d'), user_id=current_user.id)
        db.session.add(log)
        db.session.commit()
        flash('Log created successfully!', 'success')
        return redirect(url_for('views.view', log_id=log.id))
    except ValueError:
        # Catch any parsing errors and inform the user
        flash('Invalid date format. Please select a valid date.', 'error')
        return redirect(url_for('views.add_date'))

@views.route('/add')
def add():
    foods = Food.query.all()
    return render_template("add.html", foods=foods, food=None)

@views.route('/add', methods=['POST'])
def add_post():
    food_id = request.form.get('food-id')  # Checks if we're editing an existing food item
    food_name = request.form.get('food-name')
    proteins = request.form.get('protein')
    carbs = request.form.get('carbohydrates')
    fats = request.form.get('fat')

    # If we're adding a new food (not updating)
    if food_id:
        # Skip "already exists" check for current food being updated
        food = Food.query.get_or_404(food_id)
        if food.name != food_name:
            # Only check for existing food if the name is being changed
            existing_food = Food.query.filter_by(name=food_name).first()
            if existing_food:
                flash('This food item already exists!', 'warning')
                return redirect(url_for('views.add'))

        # Update existing food item
        food.name = food_name
        food.proteins = proteins
        food.carbs = carbs
        food.fats = fats
    else:
        # Adding a new food item
        existing_food = Food.query.filter_by(name=food_name).first()
        if existing_food:
            flash('This food item already exists!', 'warning')
            return redirect(url_for('views.add'))
        
        # Create a new food entry if it doesn't already exist
        new_food = Food(
            name=food_name,
            proteins=proteins,
            carbs=carbs,
            fats=fats
        )
        db.session.add(new_food)
    
    # Commit changes to the database
    try:
        db.session.commit()
        flash('Food item updated successfully!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('An error occurred while saving the food item. Please try again.', 'danger')

    return redirect(url_for('views.add'))

@views.route('/delete_food/<int:food_id>')
def delete_food(food_id):
    food = Food.query.get_or_404(food_id)
    if food:
        db.session.delete(food)
        db.session.commit()
        flash('Food item deleted successfully!', 'success')
    else:
        flash('Food item not found.', 'warning')
    return redirect(url_for('views.add'))

@views.route('/edit_food/<int:food_id>')
def edit_food(food_id):
    food = Food.query.get_or_404(food_id)
    foods = Food.query.all()
    return render_template('add.html', food=food, foods=foods)

@views.route('/view/<int:log_id>')
@login_required
def view(log_id):
    log = Log.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    foods = Food.query.all()

    totals = {
        'proteins' : 0,
        'carbs' : 0,
        'fat' : 0,
        'calories' : 0
    }

    for food in log.foods:
        totals['proteins'] += food.proteins
        totals['carbs'] += food.carbs
        totals['fat']  += food.fats
        totals['calories'] += food.calories

    return render_template("view.html", foods=foods, log=log, totals=totals)



@views.route('/add_food_to_log/<int:log_id>', methods=['POST'])
def add_food_to_log(log_id):
    log = Log.query.get_or_404(log_id)
    selected_food = request.form.get('food-select')
    food = Food.query.get(int(selected_food))
    log.foods.append(food)
    db.session.commit()

    return redirect(url_for('views.view', log_id=log_id))

@views.route('/remove_food_from_log/<int:log_id>/<int:food_id>')
def remove_food_from_log(log_id, food_id):
    log = Log.query.get(log_id)
    food = Food.query.get(food_id)
    log.foods.remove(food)
    db.session.commit()
    return redirect(url_for('views.view', log_id=log_id))