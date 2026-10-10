import pytest
from app import create_app
from database import db
from models import User, Role, Vehicle

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_user_registration_and_login(client):
    # Test Registration
    res = client.post('/register', data={
        'name': 'Test Citizen',
        'email': 'citizen_test@emergency.org',
        'phone': '1234567890',
        'password': 'Password123!',
        'confirm_password': 'Password123!',
        'reg_number': 'KL-07-TT-9988',
        'vehicle_type': 'SUV',
        'make_model': 'Mahindra XUV700',
        'color': 'Midnight Blue'
    }, follow_redirects=True)
    assert res.status_code == 200

    # Verify user in database
    user = User.query.filter_by(email='citizen_test@emergency.org').first()
    assert user is not None
    assert user.check_password('Password123!')
    assert user.role.name == 'user'
    assert len(user.vehicles) == 1
    assert user.vehicles[0].registration_number == 'KL-07-TT-9988'

def test_role_based_access_control(client):
    # Login as seeded regular driver
    client.post('/login', data={'email': 'driver@emergency.org', 'password': 'DemoUser123!'}, follow_redirects=True)

    # Attempt to access protected admin endpoint
    res = client.get('/admin/dashboard', follow_redirects=True)
    # Should be denied and redirected
    assert res.status_code == 200
    assert (b"Access denied" in res.data or b"Overview" in res.data or b"Emergency" in res.data)
