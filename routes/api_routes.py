from flask import Blueprint, jsonify, request
from flask_login import current_user
from database import db
from models import EmergencyTrip, Hospital, LocationUpdate
from services.hospital_service import find_nearby_hospitals
from services.routing_service import get_route_and_eta
from services.demo_simulator import step_simulation_progress

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/hospitals/nearby', methods=['GET'])
def get_nearby_hospitals():
    try:
        lat = float(request.args.get('lat', 28.5672))
        lng = float(request.args.get('lng', 77.2100))
        radius = float(request.args.get('radius')) if request.args.get('radius') else None
        query = request.args.get('q', None)
        city = request.args.get('city', None)
        scope = request.args.get('scope', 'all_india')
        emergency_type = request.args.get('emergency_type', None)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid lat/lng parameters'}), 400

    hospitals = find_nearby_hospitals(
        lat=lat, 
        lng=lng, 
        radius_km=radius, 
        search_query=query, 
        emergency_type=emergency_type, 
        city_filter=city if city != 'All India' and city != 'All' else None, 
        scope=scope
    )
    return jsonify({
        'success': True,
        'count': len(hospitals),
        'hospitals': hospitals
    })

@api_bp.route('/api/routing/route', methods=['GET'])
def get_route():
    try:
        origin_lat = float(request.args.get('origin_lat'))
        origin_lng = float(request.args.get('origin_lng'))
        dest_lat = float(request.args.get('dest_lat'))
        dest_lng = float(request.args.get('dest_lng'))
    except (ValueError, TypeError, KeyError):
        return jsonify({'error': 'Origin and destination coordinates are required'}), 400

    route_data = get_route_and_eta(origin_lat, origin_lng, dest_lat, dest_lng)
    return jsonify(route_data)

@api_bp.route('/api/emergency/trip/<trip_id>/status', methods=['GET'])
def get_trip_status(trip_id):
    trip = db.session.get(EmergencyTrip, trip_id)
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404

    return jsonify({
        'success': True,
        'trip': trip.to_dict()
    })

@api_bp.route('/api/demo/simulate-step', methods=['POST'])
def simulate_step():
    data = request.get_json() or {}
    trip_id = data.get('trip_id')
    progress = data.get('progress', 0.0)

    trip = db.session.get(EmergencyTrip, trip_id)
    if not trip:
        return jsonify({'error': 'Trip not found'}), 404

    res = step_simulation_progress(trip, progress)
    return jsonify({
        'success': True,
        'result': res
    })

@api_bp.route('/api/active-emergencies', methods=['GET'])
def get_active_emergencies():
    trips = EmergencyTrip.query.filter_by(status='active').all()
    return jsonify({
        'success': True,
        'count': len(trips),
        'trips': [t.to_dict() for t in trips]
    })
