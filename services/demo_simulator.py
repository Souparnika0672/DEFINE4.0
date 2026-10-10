import math
from datetime import datetime
from database import db
from models import EmergencyTrip, LocationUpdate, HospitalAcknowledgement
from services.alert_service import dispatch_driver_vicinity_alerts
from services.routing_service import get_route_and_eta
from sockets import socketio

def step_simulation_progress(trip, progress_pct):
    """
    Advances the simulated trip along its route from 0% to 100%.
    Updates current coordinates, recalculates remaining distance and ETA,
    logs the location update, and broadcasts to live sockets.
    """
    if not trip or trip.status != 'active':
        return None

    progress_pct = max(0.0, min(100.0, float(progress_pct)))
    fraction = progress_pct / 100.0

    # Calculate intermediate coordinates
    dest_lat = trip.destination_lat or (trip.activation_lat + 0.035)
    dest_lng = trip.destination_lng or (trip.activation_lng + 0.045)
    
    current_lat = trip.activation_lat + (dest_lat - trip.activation_lat) * fraction
    current_lng = trip.activation_lng + (dest_lng - trip.activation_lng) * fraction
    
    # Jitter slightly for realistic vehicle movement
    jitter_lat = math.sin(fraction * math.pi * 4) * 0.0003
    jitter_lng = math.cos(fraction * math.pi * 4) * 0.0003
    current_lat += jitter_lat
    current_lng += jitter_lng

    # Update trip
    trip.current_lat = current_lat
    trip.current_lng = current_lng
    trip.last_location_time = datetime.utcnow()

    # Recalculate remaining distance & ETA
    total_dist = trip.distance_km or 6.5
    rem_dist = max(0.1, round(total_dist * (1.0 - fraction), 2))
    rem_eta = max(0.5, round((rem_dist / 40.0) * 60.0, 1))

    trip.estimated_time_minutes = rem_eta

    # If reached 100%, mark as reached destination
    if progress_pct >= 98.0:
        trip.status = 'reached'
        trip.completed_at = datetime.utcnow()

    # Record location point
    loc = LocationUpdate(
        trip_id=trip.id,
        latitude=current_lat,
        longitude=current_lng,
        speed_kmh=48.5,
        heading=45.0,
        accuracy_meters=4.2,
        is_simulated=True
    )
    db.session.add(loc)
    db.session.commit()

    # Broadcast updates
    payload = {
        'trip_id': trip.id,
        'latitude': current_lat,
        'longitude': current_lng,
        'progress_pct': progress_pct,
        'remaining_distance_km': rem_dist,
        'remaining_eta_min': rem_eta,
        'status': trip.status,
        'timestamp': datetime.utcnow().strftime('%H:%M:%S'),
        'vehicle_reg': trip.vehicle.registration_number if trip.vehicle else 'EP-DEMO'
    }

    socketio.emit('vehicle_moved', payload, to=f"trip_{trip.id}")
    if trip.hospital_id:
        socketio.emit('hospital_trip_update', payload, to=f"hospital_{trip.hospital_id}")
    socketio.emit('police_vehicle_moved', payload, to="police_command")

    # Dispatch vicinity alerts at key waypoints (e.g. 20%, 50%, 80%)
    if int(progress_pct) in (20, 50, 75):
        dispatch_driver_vicinity_alerts(trip, current_lat, current_lng)

    return payload
