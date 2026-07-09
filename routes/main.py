from flask import Blueprint, render_template
from models import get_all_courses

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    courses = get_all_courses()
    return render_template('index.html', courses=courses)

@main_bp.route('/courses')
def courses():
    all_courses = get_all_courses()
    return render_template('courses.html', courses=all_courses)