from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from database import db
from models import EmergencyTrip, Hospital, HospitalAcknowledgement, User
from auth import role_required
from services.audit_service import log_audit_event
from sockets import socketio

hospital_bp = Blueprint('hospital', __name__)

@hospital_bp.route('/hospital/dashboard')
@login_required
@role_required('hospital', 'admin')
def dashboard():
    hospital_id = current_user.hospital_id
    if not hospital_id:
        first_hosp = Hospital.query.first()
        hospital_id = first_hosp.id if first_hosp else None

    hospital = Hospital.query.get(hospital_id) if hospital_id else None

    if hospital:
        active_incoming = EmergencyTrip.query.filter(
            EmergencyTrip.hospital_id == hospital.id,
            EmergencyTrip.status == 'active'
        ).order_by(EmergencyTrip.started_at.desc()).all()

        recent_admissions = EmergencyTrip.query.filter(
            EmergencyTrip.hospital_id == hospital.id,
            EmergencyTrip.status.in_(['reached', 'completed'])
        ).order_by(EmergencyTrip.completed_at.desc()).limit(8).all()
    else:
        active_incoming = []
        recent_admissions = []

    return render_template('hospital/dashboard.html', 
                           hospital=hospital, 
                           active_incoming=active_incoming, 
                           recent_admissions=recent_admissions)

@hospital_bp.route('/hospital/update-capacity', methods=['POST'])
@login_required
@role_required('hospital', 'admin')
def update_capacity():
    hospital_id = current_user.hospital_id or 1
    hospital = Hospital.query.get_or_404(hospital_id)
    
    avail = int(request.form.get('available_icu_beds', hospital.available_icu_beds))
    total = int(request.form.get('total_icu_beds', hospital.total_icu_beds))

    hospital.available_icu_beds = avail
    hospital.total_icu_beds = total
    db.session.commit()

    log_audit_event(current_user.id, 'HOSPITAL_CAPACITY_UPDATED', 'hospital', str(hospital.id), 
                    details={'avail': avail, 'total': total})

    flash(f"Hospital ICU capacity updated: {avail} / {total} beds available.", 'success')
    return redirect(url_for('hospital.dashboard'))

@hospital_bp.route('/hospital/acknowledge/<trip_id>', methods=['POST'])
@login_required
@role_required('hospital', 'admin')
def acknowledge_trip(trip_id):
    trip = EmergencyTrip.query.get_or_404(trip_id)
    status_choice = request.form.get('status', 'accepted')
    notes = request.form.get('notes', '').strip()
    triage = request.form.get('triage_priority', 'critical')

    ack = HospitalAcknowledgement(
        trip_id=trip.id,
        hospital_id=trip.hospital_id,
        staff_user_id=current_user.id,
        status=status_choice,
        notes=notes,
        triage_priority=triage
    )
    db.session.add(ack)

    if status_choice == 'patient_arrived':
        trip.status = 'reached'
        trip.completed_at = datetime.utcnow()

    db.session.commit()

    socketio.emit('hospital_ack_update', {
        'trip_id': trip.id,
        'status': status_choice,
        'notes': notes,
        'triage_priority': triage,
        'hospital_name': trip.destination_hospital.name if trip.destination_hospital else 'Hospital ER Desk',
        'timestamp': datetime.utcnow().strftime('%H:%M:%S')
    }, to=f"trip_{trip.id}")

    log_audit_event(current_user.id, 'HOSPITAL_ACKNOWLEDGED', 'trip', trip.id, 
                    details={'status': status_choice, 'triage': triage, 'notes': notes})

    flash(f"Emergency Trip {trip.id} triage status recorded: {status_choice.replace('_', ' ').upper()}.", 'success')
    return redirect(url_for('hospital.dashboard'))
