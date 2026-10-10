import os
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
from database import db
from models import EmergencyTrip, LocationUpdate, HospitalAcknowledgement, Notification

_async_mode = 'gevent' if os.environ.get('FLASK_ENV') == 'production' else 'threading'
socketio = SocketIO(cors_allowed_origins="*", async_mode=_async_mode)

def init_sockets(app):
    socketio.init_app(app, async_mode=_async_mode, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    # Client connected
    pass

@socketio.on('join_trip')
def on_join_trip(data):
    trip_id = data.get('trip_id')
    if trip_id:
        join_room(f"trip_{trip_id}")
        emit('room_joined', {'trip_id': trip_id, 'status': 'connected'})

@socketio.on('leave_trip')
def on_leave_trip(data):
    trip_id = data.get('trip_id')
    if trip_id:
        leave_room(f"trip_{trip_id}")

@socketio.on('join_hospital_room')
def on_join_hospital(data):
    hospital_id = data.get('hospital_id')
    if hospital_id:
        join_room(f"hospital_{hospital_id}")
        emit('hospital_room_joined', {'hospital_id': hospital_id})

@socketio.on('join_police_channel')
def on_join_police():
    join_room("police_command")
    emit('police_channel_joined', {'status': 'active'})

@socketio.on('join_driver_channel')
def on_join_driver():
    join_room("driver_vicinity_broadcast")
    emit('driver_channel_joined', {'status': 'active'})

@socketio.on('update_location')
def on_update_location(data):
    trip_id = data.get('trip_id')
    lat = data.get('latitude')
    lng = data.get('longitude')
    speed = data.get('speed', 0.0)
    heading = data.get('heading', 0.0)
    accuracy = data.get('accuracy', 5.0)
    is_sim = data.get('is_simulated', False)

    if not trip_id or lat is None or lng is None:
        return

    trip = EmergencyTrip.query.get(trip_id)
    if not trip or trip.status != 'active':
        return

    trip.current_lat = lat
    trip.current_lng = lng
    trip.accuracy_meters = accuracy
    trip.last_location_time = datetime.utcnow()
    
    loc = LocationUpdate(
        trip_id=trip.id,
        latitude=lat,
        longitude=lng,
        speed_kmh=speed,
        heading=heading,
        accuracy_meters=accuracy,
        is_simulated=is_sim
    )
    db.session.add(loc)
    db.session.commit()

    payload = {
        'trip_id': trip.id,
        'latitude': lat,
        'longitude': lng,
        'speed_kmh': speed,
        'heading': heading,
        'accuracy_meters': accuracy,
        'timestamp': datetime.utcnow().strftime('%H:%M:%S'),
        'vehicle_reg': trip.vehicle.registration_number if trip.vehicle else 'N/A'
    }

    # Broadcast to trip subscribers, hospital room, and police command
    emit('vehicle_moved', payload, to=f"trip_{trip.id}")
    if trip.hospital_id:
        emit('hospital_trip_update', payload, to=f"hospital_{trip.hospital_id}")
    emit('police_vehicle_moved', payload, to="police_command")

