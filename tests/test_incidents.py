import pytest
from app import create_app
from database import db
from models import User, Role, Vehicle, EmergencyTrip, IncidentReport, AuditLog

@pytest.fixture
def incident_client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            driver = User.query.filter_by(email='driver@emergency.org').first()
            vehicle = driver.vehicles[0] if driver and driver.vehicles else None
            driver_id = driver.id if driver else 1
            vehicle_id = vehicle.id if vehicle else 1

            trip = EmergencyTrip(
                user_id=driver_id,
                vehicle_id=vehicle_id,
                activation_lat=9.98,
                activation_lng=76.29,
                current_lat=9.98,
                current_lng=76.29,
                status='active'
            )
            db.session.add(trip)
            db.session.commit()
            trip_id = trip.id

        yield client, driver_id, trip_id

def test_incident_reporting_and_review(incident_client):
    client, driver_id, trip_id = incident_client

    # 1. Login as Admin
    client.post('/login', data={'email': 'admin@emergency.org', 'password': 'DemoAdmin123!'}, follow_redirects=True)

    # 2. File Incident Report
    res = client.post('/incidents/report', data={
        'trip_id': trip_id,
        'reason': 'suspicious_frequent_activation',
        'evidence_notes': 'Repeated activation without proceeding towards any hospital.'
    }, follow_redirects=True)
    assert res.status_code == 200

    report = IncidentReport.query.filter_by(trip_id=trip_id).first()
    assert report is not None
    assert report.status == 'pending_review'

    # 3. Review Incident Report
    res = client.post(f'/incidents/{report.id}/review', data={
        'reviewer_action': 'warning_issued',
        'review_notes': 'First infraction. Warning issued to registered vehicle owner.'
    }, follow_redirects=True)
    assert res.status_code == 200

    report = IncidentReport.query.filter_by(id=report.id).first()
    assert report.status == 'verified_misuse'
    assert report.reviewer_action == 'warning_issued'
    assert report.resolved_at is not None
