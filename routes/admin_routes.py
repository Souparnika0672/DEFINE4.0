from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
import os
from database import db
from models import User, Role, Vehicle, Hospital, EmergencyTrip, IncidentReport, AuditLog
from auth import role_required
from services.audit_service import log_audit_event

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@login_required
@role_required('admin')
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_vehicles': Vehicle.query.count(),
        'total_hospitals': Hospital.query.count(),
        'active_emergencies': EmergencyTrip.query.filter_by(status='active').count(),
        'total_trips': EmergencyTrip.query.count(),
        'pending_incidents': IncidentReport.query.filter_by(status='pending_review').count()
    }
    
    recent_trips = EmergencyTrip.query.order_by(EmergencyTrip.started_at.desc()).limit(6).all()
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(8).all()
    
    openmap_key = current_app.config.get('OPENMAP_API_KEY', '')

    return render_template('admin/dashboard.html', 
                           stats=stats, 
                           recent_trips=recent_trips, 
                           recent_logs=recent_logs,
                           openmap_key=openmap_key)

@admin_bp.route('/admin/api-keys', methods=['POST'])
@login_required
@role_required('admin')
def update_api_keys():
    openmap_key = request.form.get('openmap_key', '').strip()
    ors_key = request.form.get('openrouteservice_key', '').strip()
    geoapify_key = request.form.get('geoapify_key', '').strip()

    # Update current runtime config
    if openmap_key:
        current_app.config['OPENMAP_API_KEY'] = openmap_key
        current_app.config['OPENROUTESERVICE_API_KEY'] = openmap_key
    if ors_key:
        current_app.config['OPENROUTESERVICE_API_KEY'] = ors_key
    if geoapify_key:
        current_app.config['GEOAPIFY_API_KEY'] = geoapify_key

    # Persist to .env file
    env_path = os.path.join(current_app.root_path, '.env')
    try:
        env_lines = [
            f"OPENMAP_API_KEY={openmap_key or ors_key or geoapify_key}",
            f"OPENROUTESERVICE_API_KEY={ors_key or openmap_key}",
            f"GEOAPIFY_API_KEY={geoapify_key or openmap_key}",
            "SECRET_KEY=emergency-pass-secure-prod-key-2026-def-789",
            "DATABASE_URL=sqlite:///emergency_pass.db",
            "FLASK_ENV=development",
            "DEMO_MODE=true"
        ]
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(env_lines) + '\n')
    except Exception as e:
        print("Notice saving .env:", e)

    log_audit_event(current_user.id, 'API_KEYS_UPDATED', 'system', 'openmaps_api')
    flash("OpenMaps API Key successfully updated and activated for real-time routing & maps!", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/admin/users')
@login_required
@role_required('admin')
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    roles = Role.query.all()
    hospitals = Hospital.query.all()
    return render_template('admin/users.html', users=all_users, roles=roles, hospitals=hospitals)

@admin_bp.route('/admin/users/<int:user_id>/update-role', methods=['POST'])
@login_required
@role_required('admin')
def update_user_role(user_id):
    user = User.query.get_or_404(user_id)
    role_id = int(request.form.get('role_id'))
    hospital_id = request.form.get('hospital_id')
    
    user.role_id = role_id
    user.hospital_id = int(hospital_id) if hospital_id and hospital_id.isdigit() else None
    db.session.commit()

    log_audit_event(current_user.id, 'USER_ROLE_UPDATED', 'user', str(user.id), details={'new_role_id': role_id})
    flash(f"Role updated for {user.name}.", 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/admin/vehicles')
@login_required
@role_required('admin')
def vehicles():
    all_vehicles = Vehicle.query.order_by(Vehicle.created_at.desc()).all()
    return render_template('admin/vehicles.html', vehicles=all_vehicles)

@admin_bp.route('/admin/vehicles/<int:vehicle_id>/verify', methods=['POST'])
@login_required
@role_required('admin')
def verify_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    action = request.form.get('action', 'approved')
    
    vehicle.is_verified = (action == 'approved')
    vehicle.verification_status = action
    db.session.commit()

    log_audit_event(current_user.id, f'VEHICLE_{action.upper()}', 'vehicle', str(vehicle.id))
    flash(f"Vehicle {vehicle.registration_number} status changed to {action}.", 'info')
    return redirect(url_for('admin.vehicles'))

@admin_bp.route('/admin/hospitals', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def hospitals():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        city = request.form.get('city', 'General')
        lat = float(request.form.get('latitude'))
        lng = float(request.form.get('longitude'))
        phone = request.form.get('phone')
        emergency_contact = request.form.get('emergency_contact')
        trauma_level = request.form.get('trauma_level', 'Level 1')
        emergency_type = request.form.get('emergency_type', '24/7 Multi-Specialty & Trauma Care')
        icu_beds = int(request.form.get('total_icu_beds', 20))
        avail_beds = int(request.form.get('available_icu_beds', 5))

        hosp = Hospital(
            name=name,
            address=address,
            city=city,
            latitude=lat,
            longitude=lng,
            phone=phone,
            emergency_contact=emergency_contact,
            trauma_level=trauma_level,
            emergency_type=emergency_type,
            total_icu_beds=icu_beds,
            available_icu_beds=avail_beds,
            is_verified=True
        )
        db.session.add(hosp)
        db.session.commit()
        log_audit_event(current_user.id, 'HOSPITAL_ADDED', 'hospital', str(hosp.id), details={'name': name})
        flash(f"Hospital {name} added to registry.", 'success')
        return redirect(url_for('admin.hospitals'))

    all_hospitals = Hospital.query.all()
    return render_template('admin/hospitals.html', hospitals=all_hospitals)

@admin_bp.route('/admin/incidents')
@login_required
@role_required('admin', 'police')
def incidents():
    all_incidents = IncidentReport.query.order_by(IncidentReport.created_at.desc()).all()
    return render_template('admin/incidents.html', incidents=all_incidents)

@admin_bp.route('/admin/audit-logs')
@login_required
@role_required('admin')
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('admin/audit_logs.html', logs=logs)
