from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from database import db
from models import IncidentReport, EmergencyTrip, User
from auth import role_required
from services.audit_service import log_audit_event

incident_bp = Blueprint('incident', __name__)

@incident_bp.route('/incidents/report', methods=['POST'])
@login_required
def report_incident():
    trip_id = request.form.get('trip_id')
    reason = request.form.get('reason', 'suspicious_frequent_activation')
    evidence_notes = request.form.get('evidence_notes', '').strip()

    trip = EmergencyTrip.query.get_or_404(trip_id)

    incident = IncidentReport(
        trip_id=trip.id,
        reported_by_id=current_user.id,
        reason=reason,
        status='pending_review',
        evidence_notes=evidence_notes
    )
    db.session.add(incident)
    db.session.commit()

    log_audit_event(current_user.id, 'INCIDENT_REPORTED', 'incident', str(incident.id), 
                    details={'trip_id': trip.id, 'reason': reason})
    
    flash(f"Incident report filed for Trip {trip.id}. An authorised administrator will review it.", 'warning')
    if current_user.is_police:
        return redirect(url_for('police.dashboard'))
    elif current_user.is_hospital:
        return redirect(url_for('hospital.dashboard'))
    return redirect(url_for('user.dashboard'))

@incident_bp.route('/incidents/<int:incident_id>/review', methods=['POST'])
@login_required
@role_required('admin', 'police')
def review_incident(incident_id):
    incident = IncidentReport.query.get_or_404(incident_id)
    action = request.form.get('reviewer_action') # 'warning_issued', 'cleared_no_violation', 'account_flagged'
    notes = request.form.get('review_notes', '').strip()

    incident.reviewer_id = current_user.id
    incident.reviewer_action = action
    incident.review_notes = notes
    incident.status = 'verified_misuse' if action in ('warning_issued', 'account_flagged') else 'cleared'
    incident.resolved_at = datetime.utcnow()
    db.session.commit()

    log_audit_event(current_user.id, 'INCIDENT_REVIEWED', 'incident', str(incident.id), 
                    details={'action': action, 'status': incident.status})
    flash(f"Incident #{incident.id} review recorded.", 'info')
    return redirect(url_for('admin.incidents'))

@incident_bp.route('/incidents/<int:incident_id>/appeal', methods=['POST'])
@login_required
def appeal_incident(incident_id):
    incident = IncidentReport.query.get_or_404(incident_id)
    appeal_notes = request.form.get('appeal_notes', '').strip()

    incident.appeal_notes = appeal_notes
    incident.status = 'appealed'
    db.session.commit()

    log_audit_event(current_user.id, 'INCIDENT_APPEALED', 'incident', str(incident.id), 
                    details={'appeal': appeal_notes})
    flash("Your explanation / appeal has been submitted for formal administrative review.", 'info')
    return redirect(url_for('user.dashboard'))
