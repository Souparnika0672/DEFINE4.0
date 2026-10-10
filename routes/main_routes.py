from flask import Blueprint, render_template, current_app
from flask_login import current_user
from models import Hospital, EmergencyTrip, Vehicle, User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    stats = {
        'total_hospitals': Hospital.query.count(),
        'active_trips': EmergencyTrip.query.filter_by(status='active').count(),
        'registered_vehicles': Vehicle.query.count(),
        'completed_trips': EmergencyTrip.query.filter(EmergencyTrip.status.in_(['reached', 'completed'])).count()
    }
    sample_hospitals = Hospital.query.limit(4).all()
    return render_template('index.html', stats=stats, sample_hospitals=sample_hospitals)

@main_bp.route('/terms')
def terms():
    return render_template('legal/terms.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('legal/privacy.html')

@main_bp.route('/settings')
def settings():
    return render_template('user/profile.html')
