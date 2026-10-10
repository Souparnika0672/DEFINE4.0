from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from database import db
from models import Vehicle, VehicleVerification, EmergencyTrip, Hospital
from auth import role_required
from services.audit_service import log_audit_event

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
    active_trip = EmergencyTrip.query.filter_by(user_id=current_user.id, status='active').first()
    past_trips = EmergencyTrip.query.filter(
        EmergencyTrip.user_id == current_user.id,
        EmergencyTrip.status != 'active'
    ).order_by(EmergencyTrip.started_at.desc()).limit(5).all()
    
    hospitals_count = Hospital.query.count()
    
    return render_template('user/dashboard.html', 
                           vehicles=vehicles, 
                           active_trip=active_trip, 
                           past_trips=past_trips,
                           hospitals_count=hospitals_count)

@user_bp.route('/vehicles')
@login_required
def vehicles():
    user_vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
    return render_template('user/vehicles.html', vehicles=user_vehicles)

@user_bp.route('/vehicles/register', methods=['GET', 'POST'])
@login_required
def register_vehicle():
    if request.method == 'POST':
        reg_number = request.form.get('reg_number', '').strip().upper()
        vehicle_type = request.form.get('vehicle_type', 'Car')
        make_model = request.form.get('make_model', '').strip()
        color = request.form.get('color', '').strip()
        notes = request.form.get('notes', '').strip()

        if not reg_number or not make_model or not color:
            flash('Please fill in all required vehicle details.', 'warning')
            return render_template('user/vehicles.html', vehicles=Vehicle.query.filter_by(user_id=current_user.id).all())

        if Vehicle.query.filter_by(registration_number=reg_number).first():
            flash(f'Vehicle with registration {reg_number} is already registered.', 'danger')
            return redirect(url_for('user.vehicles'))

        vehicle = Vehicle(
            user_id=current_user.id,
            registration_number=reg_number,
            vehicle_type=vehicle_type,
            make_model=make_model,
            color=color,
            notes=notes,
            is_verified=True, # Auto-approved for standard demo onboarding
            verification_status='approved'
        )
        db.session.add(vehicle)
        db.session.commit()
        
        log_audit_event(current_user.id, 'VEHICLE_REGISTERED', 'vehicle', str(vehicle.id), details={'reg': reg_number})
        flash(f'Vehicle {reg_number} successfully registered and ready for emergency use.', 'success')
        return redirect(url_for('user.vehicles'))

    return redirect(url_for('user.vehicles'))

@user_bp.route('/vehicles/<int:vehicle_id>/delete', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.filter_by(id=vehicle_id, user_id=current_user.id).first_or_404()
    # Check if vehicle is in an active trip
    active_trip = EmergencyTrip.query.filter_by(vehicle_id=vehicle.id, status='active').first()
    if active_trip:
        flash('Cannot delete vehicle while an active emergency trip is in progress.', 'danger')
        return redirect(url_for('user.vehicles'))

    reg = vehicle.registration_number
    db.session.delete(vehicle)
    db.session.commit()
    log_audit_event(current_user.id, 'VEHICLE_DELETED', 'vehicle', str(vehicle_id), details={'reg': reg})
    flash(f'Vehicle {reg} removed.', 'info')
    return redirect(url_for('user.vehicles'))
