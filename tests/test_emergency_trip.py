import pytest
from app import create_app
from database import db
from models import User, Role, Vehicle, Hospital, EmergencyTrip

@pytest.fixture
def app_and_client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            driver = User.query.filter_by(email='driver@emergency.org').first()
            vehicle = driver.vehicles[0] if driver and driver.vehicles else None
            hospital = Hospital.query.first()
            driver_id = driver.id if driver else None
            vehicle_id = vehicle.id if vehicle else None
            hospital_id = hospital.id if hospital else None

        yield app, client, driver_id, vehicle_id, hospital_id

def test_emergency_trip_lifecycle(app_and_client):
    app, client, user_id, vehicle_id, hospital_id = app_and_client
    
    # 1. Login
    client.post('/login', data={'email': 'driver@emergency.org', 'password': 'DemoUser123!'}, follow_redirects=True)

    # 2. Start Emergency Trip
    res = client.post('/emergency/start', data={
        'vehicle_id': vehicle_id,
        'emergency_type': 'Cardiac Emergency',
        'latitude': '9.9800',
        'longitude': '76.2900',
        'accuracy': '8.0',
        'is_simulated': 'true'
    }, follow_redirects=True)
    assert res.status_code == 200

    trip = EmergencyTrip.query.filter_by(user_id=user_id, status='active').first()
    assert trip is not None
    assert trip.id.startswith('EP-')
    assert trip.is_simulated is True

    # 3. Select Destination Hospital
    res = client.post('/emergency/select-hospital', data={
        'trip_id': trip.id,
        'hospital_id': str(hospital_id)
    }, follow_redirects=True)
    assert res.status_code == 200

    # Refresh trip
    trip = EmergencyTrip.query.get(trip.id)
    assert trip.hospital_id == hospital_id
    assert trip.distance_km > 0
    assert trip.estimated_time_minutes > 0

    # 4. Mark Patient Arrived / Complete Trip
    res = client.post(f'/emergency/trip/{trip.id}/complete', follow_redirects=True)
    assert res.status_code == 200

    trip = EmergencyTrip.query.get(trip.id)
    assert trip.status == 'completed'
    assert trip.completed_at is not None
