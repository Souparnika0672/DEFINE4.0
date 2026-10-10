from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from database import db
from models import EmergencyTrip, Vehicle, Hospital, LocationUpdate, HospitalAcknowledgement, Notification
from services.hospital_service import find_nearby_hospitals, haversine_distance, estimate_travel_time
from services.routing_service import get_route_and_eta
from services.alert_service import dispatch_multi_party_emergency_alerts, expire_trip_alerts
from services.audit_service import log_audit_event
from sockets import socketio

emergency_bp = Blueprint('emergency', __name__)

@emergency_bp.route('/emergency/activate')
def activate():
    if current_user.is_authenticated:
        existing_trip = EmergencyTrip.query.filter_by(user_id=current_user.id, status='active').first()
        if existing_trip:
            if not existing_trip.hospital_id:
                return redirect(url_for('emergency.select_hospitals_view', trip_id=existing_trip.id))
            return redirect(url_for('emergency.live_trip', trip_id=existing_trip.id))
        vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
    else:
        vehicles = []

    return render_template('emergency/activate.html', vehicles=vehicles)

@emergency_bp.route('/emergency/start', methods=['POST'])
def start_emergency():
    user_id = current_user.id if current_user.is_authenticated else 1
    
    vehicle_id = request.form.get('vehicle_id')
    emergency_type = request.form.get('emergency_type', 'Cardiac Arrest / Acute Chest Pain')
    severity_level = request.form.get('severity_level', 'Critical Immediate')
    patient_name = request.form.get('patient_name', '').strip()
    patient_phone = request.form.get('patient_phone', '').strip()
    patient_notes = request.form.get('patient_notes', '').strip()
    is_simulated = bool(request.form.get('is_simulated') == 'true')
    
    try:
        lat = float(request.form.get('latitude', 28.5672))
        lng = float(request.form.get('longitude', 77.2100))
    except (ValueError, TypeError):
        lat, lng = 28.5672, 77.2100

    accuracy = float(request.form.get('accuracy', 10.0))

    if vehicle_id and vehicle_id.isdigit():
        vehicle = db.session.get(Vehicle, int(vehicle_id))
    else:
        vehicle = Vehicle.query.filter_by(user_id=user_id).first() if current_user.is_authenticated else None

    trip = EmergencyTrip(
        user_id=user_id,
        vehicle_id=vehicle.id if vehicle else None,
        activation_lat=lat,
        activation_lng=lng,
        current_lat=lat,
        current_lng=lng,
        emergency_type=emergency_type,
        severity_level=severity_level,
        specialty_required=emergency_type.split('/')[0].strip(),
        patient_name=patient_name or (current_user.name if current_user.is_authenticated else 'Emergency Patient'),
        patient_phone=patient_phone or (current_user.phone if current_user.is_authenticated else 'N/A'),
        patient_notes=patient_notes,
        is_simulated=is_simulated,
        accuracy_meters=accuracy,
        status='active',
        police_clearance_status='pending_clearance',
        police_clearance_notes='Emergency Request Dispatched to Police Traffic Control',
        hospital_prep_status='notifying_er',
        hospital_prep_notes='Searching closest specialized emergency facilities across India...'
    )
    db.session.add(trip)
    db.session.flush()

    loc = LocationUpdate(
        trip_id=trip.id,
        latitude=lat,
        longitude=lng,
        speed_kmh=0.0,
        accuracy_meters=accuracy,
        is_simulated=is_simulated
    )
    db.session.add(loc)
    db.session.commit()

    log_audit_event(user_id, 'EMERGENCY_ACTIVATED', 'trip', trip.id, 
                    details={'lat': lat, 'lng': lng, 'emergency_type': emergency_type, 'severity': severity_level})

    flash(f"EMERGENCY SOS INITIATED: Tailored hospital recommendations across India for {emergency_type.split('/')[0].strip()} are listed below.", 'danger')
    return redirect(url_for('emergency.select_hospitals_view', trip_id=trip.id))

@emergency_bp.route('/emergency/hospitals')
def select_hospitals_view():
    trip_id = request.args.get('trip_id')
    if not trip_id:
        if current_user.is_authenticated:
            active_trip = EmergencyTrip.query.filter_by(user_id=current_user.id, status='active').first()
            if active_trip:
                trip_id = active_trip.id
        if not trip_id:
            flash('Activate emergency mode first.', 'warning')
            return redirect(url_for('emergency.activate'))

    trip = db.session.get(EmergencyTrip, trip_id)
    if not trip:
        flash('Emergency trip not found.', 'danger')
        return redirect(url_for('emergency.activate'))
    
    city_filter = request.args.get('city', 'All India')
    scope = request.args.get('scope', 'all_india')
    search_q = request.args.get('q', '').strip()

    # Query tailored hospitals matched to this emergency type across India
    tailored_hospitals = find_nearby_hospitals(
        lat=trip.current_lat, 
        lng=trip.current_lng, 
        radius_km=50.0 if scope == 'nearby' else None, 
        search_query=search_q if search_q else None,
        emergency_type=trip.emergency_type,
        city_filter=city_filter if city_filter != 'All India' and city_filter != 'All' else None,
        scope=scope
    )
    
    available_cities = [
        'All India', 'Delhi NCR', 'Mumbai', 'Bengaluru', 'Chennai', 
        'Hyderabad', 'Kolkata', 'Kochi / Kerala', 'Pune', 'Ahmedabad', 
        'Trivandrum / Kerala', 'Kozhikode / Calicut', 'Chandigarh', 'Jaipur / Rajasthan', 'Lucknow / Uttar Pradesh'
    ]

    return render_template('emergency/hospitals.html', 
                           trip=trip, 
                           hospitals=tailored_hospitals,
                           selected_city=city_filter,
                           selected_scope=scope,
                           search_q=search_q,
                           available_cities=available_cities)

@emergency_bp.route('/emergency/select-hospital', methods=['POST'])
def select_hospital():
    trip_id = request.form.get('trip_id')
    hospital_id = request.form.get('hospital_id')
    custom_name = request.form.get('custom_name')
    custom_lat = request.form.get('custom_lat')
    custom_lng = request.form.get('custom_lng')
    custom_addr = request.form.get('custom_addr', 'Emergency Medical Center')

    trip = db.session.get(EmergencyTrip, trip_id)
    if not trip:
        flash('Trip not found.', 'danger')
        return redirect(url_for('main.index'))

    if hospital_id and hospital_id.isdigit():
        hospital = db.session.get(Hospital, int(hospital_id))
        if hospital:
            trip.hospital_id = hospital.id
            trip.destination_lat = hospital.latitude
            trip.destination_lng = hospital.longitude
    elif custom_lat and custom_lng:
        h_lat = float(custom_lat)
        h_lng = float(custom_lng)
        hospital = Hospital.query.filter_by(name=custom_name).first()
        if not hospital:
            hospital = Hospital(
                name=custom_name or 'Emergency Care Center',
                address=custom_addr,
                city='Pan-India Registry',
                latitude=h_lat,
                longitude=h_lng,
                phone='+91 11 2658 8500',
                emergency_contact='108',
                trauma_level='Level 1 / 2 ER',
                is_verified=True,
                is_demo=False
            )
            db.session.add(hospital)
            db.session.flush()
        trip.hospital_id = hospital.id
        trip.destination_lat = h_lat
        trip.destination_lng = h_lng

    # Calculate road distance & ETA
    if trip.destination_lat and trip.destination_lng:
        route_data = get_route_and_eta(trip.current_lat, trip.current_lng, trip.destination_lat, trip.destination_lng)
        trip.distance_km = route_data.get('distance_km', 0.0)
        trip.estimated_time_minutes = route_data.get('duration_min', 0.0)

    trip.police_clearance_status = 'pending_clearance'
    trip.police_clearance_notes = 'Traffic Clearance Request Dispatched to Police Command'
    trip.hospital_prep_status = 'bay_prepared'
    trip.hospital_prep_notes = f"Pre-Arrival Alert Sent to {trip.destination_hospital.name if trip.destination_hospital else 'ER'}"
    
    db.session.commit()

    # MULTI-PARTY SIMULTANEOUS BROADCAST (Police, Hospital, Drivers)
    dispatch_multi_party_emergency_alerts(trip)

    log_audit_event(trip.user_id, 'HOSPITAL_SELECTED', 'trip', trip.id, 
                    details={'hospital': trip.destination_hospital.name if trip.destination_hospital else 'N/A', 
                             'distance_km': trip.distance_km, 'eta_min': trip.estimated_time_minutes})

    flash(f"Emergency route locked to {trip.destination_hospital.name if trip.destination_hospital else 'Hospital'}. Traffic Clearance & Hospital ER Pre-Alerts dispatched!", 'success')
    return redirect(url_for('emergency.live_trip', trip_id=trip.id))

@emergency_bp.route('/emergency/trip/<trip_id>')
def live_trip(trip_id):
    trip = db.session.get(EmergencyTrip, trip_id)
    if not trip:
        flash('Emergency trip not found.', 'danger')
        return redirect(url_for('main.index'))

    if not trip.hospital_id or not trip.destination_lat:
        return redirect(url_for('emergency.select_hospitals_view', trip_id=trip.id))

    route_info = get_route_and_eta(trip.current_lat, trip.current_lng, trip.destination_lat, trip.destination_lng)
    latest_ack = HospitalAcknowledgement.query.filter_by(trip_id=trip.id).order_by(HospitalAcknowledgement.timestamp.desc()).first()
    alt_hospitals = Hospital.query.filter(Hospital.id != trip.hospital_id).limit(30).all()

    return render_template('emergency/live_trip.html', 
                           trip=trip, 
                           route_info=route_info, 
                           latest_ack=latest_ack,
                           alt_hospitals=alt_hospitals)

@emergency_bp.route('/emergency/trip/<trip_id>/change-hospital', methods=['POST'])
def change_hospital(trip_id):
    trip = db.session.get(EmergencyTrip, trip_id)
    if not trip:
        flash('Emergency trip not found.', 'danger')
        return redirect(url_for('main.index'))

    new_hospital_id = int(request.form.get('new_hospital_id'))
    hospital = db.session.get(Hospital, new_hospital_id)
    if not hospital:
        flash('Selected hospital not found.', 'danger')
        return redirect(url_for('emergency.live_trip', trip_id=trip.id))

    trip.hospital_id = hospital.id
    trip.destination_lat = hospital.latitude
    trip.destination_lng = hospital.longitude

    route_data = get_route_and_eta(trip.current_lat, trip.current_lng, hospital.latitude, hospital.longitude)
    trip.distance_km = route_data.get('distance_km', 0.0)
    trip.estimated_time_minutes = route_data.get('duration_min', 0.0)

    db.session.commit()

    dispatch_multi_party_emergency_alerts(trip)

    flash(f"Destination updated to {hospital.name}. Route and multi-party alerts refreshed.", 'info')
    return redirect(url_for('emergency.live_trip', trip_id=trip.id))

@emergency_bp.route('/emergency/trip/<trip_id>/complete', methods=['POST'])
def complete_trip(trip_id):
    trip = db.session.get(EmergencyTrip, trip_id)
    if not trip:
        flash('Emergency trip not found.', 'danger')
        return redirect(url_for('main.index'))

    trip.status = 'completed'
    trip.completed_at = datetime.utcnow()
    db.session.commit()

    expire_trip_alerts(trip.id)
    log_audit_event(trip.user_id, 'TRIP_COMPLETED', 'trip', trip.id)
    
    flash('Emergency Transit Completed. Patient arrived safely at hospital ER.', 'success')
    return redirect(url_for('main.index'))

@emergency_bp.route('/emergency/trip/<trip_id>/cancel', methods=['POST'])
def cancel_trip(trip_id):
    trip = db.session.get(EmergencyTrip, trip_id)
    if not trip:
        flash('Emergency trip not found.', 'danger')
        return redirect(url_for('main.index'))

    reason = request.form.get('reason', 'User cancelled emergency trip')
    trip.status = 'cancelled'
    trip.cancelled_at = datetime.utcnow()
    trip.cancellation_reason = reason
    db.session.commit()

    expire_trip_alerts(trip.id)
    log_audit_event(trip.user_id, 'TRIP_CANCELLED', 'trip', trip.id, details={'reason': reason})

    flash('Emergency Trip has been cancelled.', 'info')
    return redirect(url_for('main.index'))
