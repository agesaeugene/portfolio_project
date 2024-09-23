from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from website.models import Food, Log
from .extensions import db
from sqlalchemy.exc import IntegrityError  
from datetime import datetime
from weasyprint import HTML
import os

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
@login_required
def add():
    foods = Food.query.filter_by(user_id=current_user.id).all()
    return render_template("add.html", foods=foods, food=None)

@views.route('/add', methods=['POST'])
@login_required
def add_post():
    food_id = request.form.get('food-id')
    food_name = request.form.get('food-name')
    proteins = request.form.get('protein')
    carbs = request.form.get('carbohydrates')
    fats = request.form.get('fat')

    if food_id:
        # Editing an existing food
        food = Food.query.get_or_404(food_id)
        if food.user_id != current_user.id:
            flash("You don't have permission to edit this food item.", 'danger')
            return redirect(url_for('views.add'))

        food.name = food_name
        food.proteins = proteins
        food.carbs = carbs
        food.fats = fats
    else:
        # Adding a new food
        existing_food = Food.query.filter_by(name=food_name, user_id=current_user.id).first()
        if existing_food:
            flash('You have already added this food item!', 'warning')
            return redirect(url_for('views.add'))

        new_food = Food(
            name=food_name,
            proteins=proteins,
            carbs=carbs,
            fats=fats,
            user_id=current_user.id  # Save the current user's ID
        )
        db.session.add(new_food)

    try:
        db.session.commit()
        flash('Food item added & updated successfully!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('An error occurred while saving the food item.', 'danger')

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
@login_required
def edit_food(food_id):
    food = Food.query.filter_by(id=food_id, user_id=current_user.id).first_or_404()
    
    # Fetch only the foods added by the current user
    foods = Food.query.filter_by(user_id=current_user.id).all()
    return render_template('add.html', food=food, foods=foods)

@views.route('/view/<int:log_id>')
@login_required
def view(log_id):
    # Fetching the log and filtering the food added by the currect user
    log = Log.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    foods = Food.query.filter_by(user_id=current_user.id).all()

    # Calculating the totals for proteins, carbs, fats, and calories
    totals = {
        'proteins' : 0,
        'carbs' : 0,
        'fat' : 0,
        'calories' : 0
    }

    # Update totals based on the foods in the log
    for food in log.foods:
        totals['proteins'] += food.proteins
        totals['carbs'] += food.carbs
        totals['fat']  += food.fats
        totals['calories'] += food.calories

    # Render the view template with only the current user's foods
    return render_template("view.html", foods=foods, log=log, totals=totals)

@views.route('/add_food_to_log/<int:log_id>', methods=['POST'])
@login_required
def add_food_to_log(log_id):
    log = Log.query.get_or_404(log_id)
    selected_food = request.form.get('food-select')
    food = Food.query.get(int(selected_food))
    if food and log:
        log.foods.append(food)
        db.session.commit()
    return redirect(url_for('views.view', log_id=log_id))

    return redirect(url_for('views.view', log_id=log_id))

@views.route('/remove_food_from_log/<int:log_id>/<int:food_id>')
def remove_food_from_log(log_id, food_id):
    log = Log.query.get(log_id)
    food = Food.query.get(food_id)
    log.foods.remove(food)
    db.session.commit()
    return redirect(url_for('views.view', log_id=log_id))

@views.route('/download_summary')
@login_required
def download_summary():
    # Fetch all logs for the current user
    logs = Log.query.filter_by(user_id=current_user.id).order_by(Log.date.desc()).all()

    # Prepare a summary of nutrients for the month
    log_summaries = []
    total_proteins = total_carbs = total_fat = total_calories = 0

    for log in logs:
        log_proteins = log_carbs = log_fat = log_calories = 0

        for food in log.foods:
            log_proteins += food.proteins
            log_carbs += food.carbs
            log_fat += food.fats
            log_calories += food.calories

        log_summaries.append({
            'date': log.date.strftime('%B %d, %Y'),
            'proteins': log_proteins,
            'carbs': log_carbs,
            'fat': log_fat,
            'calories': log_calories,
        })

        total_proteins += log_proteins
        total_carbs += log_carbs
        total_fat += log_fat
        total_calories += log_calories

    # Render the PDF-friendly HTML template
    html = render_template('monthly_summary_pdf.html', logs=log_summaries, 
                           total_proteins=total_proteins, total_carbs=total_carbs, 
                           total_fat=total_fat, total_calories=total_calories)

    # Convert the HTML to PDF
    pdf = HTML(string=html).write_pdf()

    # Generate a downloadable response
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=monthly_summary.pdf'

    return response