from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from database import db
from models import EmergencyTrip, IncidentReport, AuditLog
from auth import role_required
from services.audit_service import log_audit_event
from sockets import socketio

police_bp = Blueprint('police', __name__)

@police_bp.route('/police/dashboard')
@login_required
@role_required('police', 'admin')
def dashboard():
    active_trips = EmergencyTrip.query.filter_by(status='active').order_by(EmergencyTrip.started_at.desc()).all()
    recent_trips = EmergencyTrip.query.filter(EmergencyTrip.status.in_(['reached', 'completed', 'cancelled'])).order_by(EmergencyTrip.started_at.desc()).limit(10).all()
    pending_incidents = IncidentReport.query.filter_by(status='pending_review').all()

    return render_template('police/dashboard.html', 
                           active_trips=active_trips, 
                           recent_trips=recent_trips, 
                           pending_incidents=pending_incidents)

@police_bp.route('/police/traffic-clearance/<trip_id>', methods=['POST'])
@login_required
@role_required('police', 'admin')
def update_traffic_clearance(trip_id):
    trip = EmergencyTrip.query.get_or_404(trip_id)
    action = request.form.get('clearance_action', 'corridor_cleared') # corridor_cleared, traffic_police_deployed, normal_traffic
    notes = request.form.get('police_notes', '').strip()

    status_labels = {
        'corridor_cleared': 'Green-Wave Signal Corridor Active (Roads Cleared)',
        'traffic_police_deployed': 'Traffic Escort / Intersection Interceptors Deployed',
        'normal_traffic': 'Monitoring Route (Normal Flow)'
    }

    trip.police_clearance_status = action
    trip.police_clearance_notes = notes or status_labels.get(action, 'Clearance in Progress')
    trip.police_action_time = datetime.utcnow()
    db.session.commit()

    # Emit live clearance update to Patient/Driver live trip screen and police channel
    socketio.emit('police_clearance_update', {
        'trip_id': trip.id,
        'status': action,
        'status_text': trip.police_clearance_notes,
        'police_badge': current_user.badge_number or 'Traffic Command #1',
        'timestamp': datetime.utcnow().strftime('%H:%M:%S')
    }, to=f"trip_{trip.id}")

    log_audit_event(current_user.id, 'POLICE_TRAFFIC_CLEARED', 'trip', trip.id, 
                    details={'status': action, 'notes': trip.police_clearance_notes})

    flash(f"Traffic clearance status for Trip {trip.id} set to: {trip.police_clearance_notes}", 'success')
    return redirect(url_for('police.dashboard'))

@police_bp.route('/police/audit')
@login_required
@role_required('police', 'admin')
def audit_view():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(50).all()
    incidents = IncidentReport.query.order_by(IncidentReport.created_at.desc()).all()
    return render_template('police/audit.html', logs=logs, incidents=incidents)
