from datetime import datetime
from database import db
from models import Notification, EmergencyTrip
from sockets import socketio

def dispatch_multi_party_emergency_alerts(trip):
    """
    Simultaneously dispatches emergency notifications to:
    1. Police Traffic Command -> Requests road clearance & green wave corridor
    2. Selected Hospital ER Desk -> Pre-arrival triage & bay preparation
    3. Nearby Drivers & Road Users -> Proximity warning to yield fast lane
    """
    vehicle_info = f"{trip.vehicle.make_model} ({trip.vehicle.registration_number})" if trip.vehicle else "Private Emergency Vehicle"
    hospital_name = trip.destination_hospital.name if trip.destination_hospital else "Nearest Emergency Center"
    patient_display = trip.patient_name or (trip.user.name if trip.user else "Patient")

    # 1. Police Traffic Clearance Request
    police_msg = f"TRAFFIC CLEARANCE REQUEST: Emergency transit for {trip.emergency_type} ({vehicle_info}) en route to {hospital_name}. ETA: {trip.estimated_time_minutes} mins. Requesting route green-wave clearance."
    notif_police = Notification(
        trip_id=trip.id,
        recipient_type='police',
        recipient_id='police_traffic_command',
        channel='in_app_socket',
        message=police_msg,
        status='delivered'
    )
    db.session.add(notif_police)

    police_payload = {
        'trip_id': trip.id,
        'vehicle_reg': trip.vehicle.registration_number if trip.vehicle else 'EMERGENCY-VEHICLE',
        'vehicle_type': trip.vehicle.vehicle_type if trip.vehicle else 'Car',
        'vehicle_model': trip.vehicle.make_model if trip.vehicle else 'N/A',
        'vehicle_color': trip.vehicle.color if trip.vehicle else 'N/A',
        'patient_name': patient_display,
        'patient_phone': trip.patient_phone or (trip.user.phone if trip.user else 'N/A'),
        'emergency_type': trip.emergency_type,
        'severity_level': trip.severity_level,
        'hospital_name': hospital_name,
        'distance_km': trip.distance_km,
        'eta_minutes': trip.estimated_time_minutes,
        'current_lat': trip.current_lat,
        'current_lng': trip.current_lng,
        'destination_lat': trip.destination_lat,
        'destination_lng': trip.destination_lng,
        'police_clearance_status': trip.police_clearance_status,
        'timestamp': datetime.utcnow().strftime('%H:%M:%S'),
        'is_simulated': trip.is_simulated
    }
    socketio.emit('new_emergency_traffic_request', police_payload, to='police_command')

    # 2. Hospital ER Pre-Arrival Notification
    if trip.hospital_id:
        hosp_msg = f"INCOMING ER PREPARATION: {trip.emergency_type} arriving via {vehicle_info}. ETA: {trip.estimated_time_minutes} min. Patient: {patient_display}."
        notif_hosp = Notification(
            trip_id=trip.id,
            recipient_type='hospital',
            recipient_id=str(trip.hospital_id),
            channel='in_app_socket',
            message=hosp_msg,
            status='delivered'
        )
        db.session.add(notif_hosp)

        hosp_payload = {
            'trip_id': trip.id,
            'vehicle_reg': trip.vehicle.registration_number if trip.vehicle else 'EMERGENCY-VEHICLE',
            'vehicle_type': trip.vehicle.vehicle_type if trip.vehicle else 'Car',
            'patient_name': patient_display,
            'patient_phone': trip.patient_phone or (trip.user.phone if trip.user else 'N/A'),
            'emergency_type': trip.emergency_type,
            'severity_level': trip.severity_level,
            'patient_notes': trip.patient_notes,
            'distance_km': trip.distance_km,
            'eta_minutes': trip.estimated_time_minutes,
            'current_lat': trip.current_lat,
            'current_lng': trip.current_lng,
            'started_at': trip.started_at.strftime('%H:%M:%S') if trip.started_at else 'Just now',
            'is_simulated': trip.is_simulated
        }
        socketio.emit('incoming_emergency_alert', hosp_payload, to=f"hospital_{trip.hospital_id}")

    # 3. Road Vicinity Driver Broadcast
    driver_msg = f"EMERGENCY ALERT: Active medical transit {vehicle_info} heading to {hospital_name}. Stay alert, clear fast lane, and give way only when safe."
    notif_driver = Notification(
        trip_id=trip.id,
        recipient_type='driver_vicinity',
        recipient_id='road_corridor_broadcast',
        channel='in_app_socket',
        message=driver_msg,
        status='delivered'
    )
    db.session.add(notif_driver)

    driver_payload = {
        'trip_id': trip.id,
        'vehicle_reg': trip.vehicle.registration_number if trip.vehicle else 'EMERGENCY-VEHICLE',
        'hospital_name': hospital_name,
        'distance_km': trip.distance_km,
        'eta_minutes': trip.estimated_time_minutes,
        'message': driver_msg,
        'timestamp': datetime.utcnow().strftime('%H:%M:%S')
    }
    socketio.emit('driver_proximity_alert', driver_payload, to='driver_vicinity_broadcast')

    db.session.commit()

# Aliases for backward compatibility
def dispatch_hospital_emergency_notification(trip):
    return dispatch_multi_party_emergency_alerts(trip)

def dispatch_driver_vicinity_alerts(trip, current_lat=None, current_lng=None):
    return dispatch_multi_party_emergency_alerts(trip)

def expire_trip_alerts(trip_id):
    payload = {
        'trip_id': trip_id,
        'status': 'ended',
        'timestamp': datetime.utcnow().strftime('%H:%M:%S')
    }
    socketio.emit('trip_ended_signal', payload, to='driver_vicinity_broadcast')
    socketio.emit('trip_ended_signal', payload, to="police_command")
