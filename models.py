import uuid
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from database import db

def generate_trip_id():
    return f"EP-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # 'user', 'hospital', 'police', 'admin'
    description = db.Column(db.String(255))
    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f"<Role {self.name}>"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_demo_account = db.Column(db.Boolean, default=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=True)
    badge_number = db.Column(db.String(50), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicles = db.relationship('Vehicle', backref='owner', lazy=True, cascade="all, delete-orphan")
    trips = db.relationship('EmergencyTrip', backref='user', lazy=True, foreign_keys='EmergencyTrip.user_id')
    incident_reports_filed = db.relationship('IncidentReport', backref='reporter', lazy=True, foreign_keys='IncidentReport.reported_by_id')
    incident_reviews = db.relationship('IncidentReport', backref='reviewer', lazy=True, foreign_keys='IncidentReport.reviewer_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, *role_names):
        if not self.role:
            return False
        return self.role.name in role_names

    @property
    def is_admin(self):
        return self.has_role('admin')

    @property
    def is_hospital(self):
        return self.has_role('hospital')

    @property
    def is_police(self):
        return self.has_role('police')

    @property
    def is_user(self):
        return self.has_role('user')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role.name if self.role else None,
            'is_active': self.is_active,
            'hospital_id': self.hospital_id,
            'badge_number': self.badge_number,
            'department': self.department,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Hospital(db.Model):
    __tablename__ = 'hospitals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    address = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), default='General')
    latitude = db.Column(db.Float, nullable=False, index=True)
    longitude = db.Column(db.Float, nullable=False, index=True)
    phone = db.Column(db.String(30), nullable=False)
    emergency_contact = db.Column(db.String(30), nullable=True)
    trauma_level = db.Column(db.String(20), default='Level 1') # Level 1, Level 2, General ER
    emergency_type = db.Column(db.String(100), default='24/7 Multi-Specialty & Trauma Care')
    specialties_json = db.Column(db.Text, default='["cardiac", "trauma", "stroke", "general"]')
    total_icu_beds = db.Column(db.Integer, default=20)
    available_icu_beds = db.Column(db.Integer, default=6)
    is_verified = db.Column(db.Boolean, default=True)
    is_demo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    staff_members = db.relationship('User', backref='hospital', lazy=True, foreign_keys='User.hospital_id')
    incoming_trips = db.relationship('EmergencyTrip', backref='destination_hospital', lazy=True, foreign_keys='EmergencyTrip.hospital_id')
    acknowledgements = db.relationship('HospitalAcknowledgement', backref='hospital', lazy=True)

    @property
    def specialties(self):
        try:
            return json.loads(self.specialties_json or '[]')
        except Exception:
            return ['general']

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'phone': self.phone,
            'emergency_contact': self.emergency_contact,
            'trauma_level': self.trauma_level,
            'emergency_type': self.emergency_type,
            'specialties': self.specialties,
            'total_icu_beds': self.total_icu_beds,
            'available_icu_beds': self.available_icu_beds,
            'is_verified': self.is_verified,
            'is_demo': self.is_demo
        }

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registration_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    vehicle_type = db.Column(db.String(30), nullable=False)
    make_model = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(30), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    verifications = db.relationship('VehicleVerification', backref='vehicle', lazy=True, cascade="all, delete-orphan")
    trips = db.relationship('EmergencyTrip', backref='vehicle', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'registration_number': self.registration_number,
            'vehicle_type': self.vehicle_type,
            'make_model': self.make_model,
            'color': self.color,
            'is_verified': self.is_verified,
            'verification_status': self.verification_status,
            'owner_name': self.owner.name if self.owner else None,
            'owner_phone': self.owner.phone if self.owner else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }

class VehicleVerification(db.Model):
    __tablename__ = 'vehicle_verifications'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    verified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False)
    document_reference = db.Column(db.String(100), nullable=True)
    reviewer_comments = db.Column(db.Text, nullable=True)
    verified_at = db.Column(db.DateTime, default=datetime.utcnow)

    verifier = db.relationship('User', foreign_keys=[verified_by_id])

class EmergencyTrip(db.Model):
    __tablename__ = 'emergency_trips'
    id = db.Column(db.String(32), primary_key=True, default=generate_trip_id)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=True)
    
    # Status: 'active', 'reached', 'completed', 'cancelled'
    status = db.Column(db.String(20), default='active', index=True)
    
    # Activation & coordinates
    activation_lat = db.Column(db.Float, nullable=False)
    activation_lng = db.Column(db.Float, nullable=False)
    current_lat = db.Column(db.Float, nullable=False)
    current_lng = db.Column(db.Float, nullable=False)
    destination_lat = db.Column(db.Float, nullable=True)
    destination_lng = db.Column(db.Float, nullable=True)
    
    # Metrics
    distance_km = db.Column(db.Float, default=0.0)
    estimated_time_minutes = db.Column(db.Float, default=0.0)
    
    # Emergency Details
    emergency_type = db.Column(db.String(100), default='Cardiac Arrest / Chest Pain')
    severity_level = db.Column(db.String(30), default='Critical Immediate') # Critical Immediate, High Urgent, Moderate
    specialty_required = db.Column(db.String(50), default='cardiac') # cardiac, trauma, stroke, pediatric, obstetric, general
    patient_name = db.Column(db.String(100), nullable=True)
    patient_phone = db.Column(db.String(30), nullable=True)
    patient_notes = db.Column(db.Text, nullable=True)

    # Multi-Party Coordination Statuses
    # 1. Police Road Clearance / Traffic Control Status: 'pending_clearance', 'corridor_cleared', 'traffic_police_deployed', 'normal_traffic'
    police_clearance_status = db.Column(db.String(50), default='pending_clearance')
    police_clearance_notes = db.Column(db.String(255), default='Awaiting Police Traffic Control Dispatch')
    police_action_time = db.Column(db.DateTime, nullable=True)

    # 2. Hospital ER Readiness Status: 'notifying_er', 'bay_prepared', 'specialist_standby', 'patient_arrived', 'diverted'
    hospital_prep_status = db.Column(db.String(50), default='notifying_er')
    hospital_prep_notes = db.Column(db.String(255), default='Notifying receiving Emergency Department...')

    # 3. Driver / Transport Status: 'driver_assigned', 'in_transit', 'arrived'
    driver_status = db.Column(db.String(50), default='in_transit')

    # Flags & Timestamps
    is_simulated = db.Column(db.Boolean, default=False)
    accuracy_meters = db.Column(db.Float, default=10.0)
    last_location_time = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancellation_reason = db.Column(db.String(255), nullable=True)

    # Relationships
    location_updates = db.relationship('LocationUpdate', backref='trip', lazy=True, cascade="all, delete-orphan", order_by="LocationUpdate.timestamp.asc()")
    notifications = db.relationship('Notification', backref='trip', lazy=True, cascade="all, delete-orphan")
    acknowledgements = db.relationship('HospitalAcknowledgement', backref='trip', lazy=True, cascade="all, delete-orphan")
    incident_reports = db.relationship('IncidentReport', backref='trip', lazy=True)

    def to_dict(self):
        latest_ack = self.acknowledgements[-1] if self.acknowledgements else None
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Citizen',
            'user_phone': self.user.phone if self.user else (self.patient_phone or 'N/A'),
            'patient_name': self.patient_name or (self.user.name if self.user else 'Patient'),
            'patient_phone': self.patient_phone or (self.user.phone if self.user else 'N/A'),
            'vehicle_id': self.vehicle_id,
            'vehicle_reg': self.vehicle.registration_number if self.vehicle else 'Private Transport',
            'vehicle_type': self.vehicle.vehicle_type if self.vehicle else 'Car',
            'vehicle_model': self.vehicle.make_model if self.vehicle else 'N/A',
            'vehicle_color': self.vehicle.color if self.vehicle else 'N/A',
            'hospital_id': self.hospital_id,
            'hospital_name': self.destination_hospital.name if self.destination_hospital else 'Not Selected Yet',
            'hospital_address': self.destination_hospital.address if self.destination_hospital else '',
            'hospital_phone': self.destination_hospital.phone if self.destination_hospital else '',
            'status': self.status,
            'activation_lat': self.activation_lat,
            'activation_lng': self.activation_lng,
            'current_lat': self.current_lat,
            'current_lng': self.current_lng,
            'destination_lat': self.destination_lat,
            'destination_lng': self.destination_lng,
            'distance_km': round(self.distance_km, 2) if self.distance_km else 0.0,
            'estimated_time_minutes': round(self.estimated_time_minutes, 1) if self.estimated_time_minutes else 0.0,
            'emergency_type': self.emergency_type,
            'severity_level': self.severity_level,
            'specialty_required': self.specialty_required,
            'patient_notes': self.patient_notes,
            'police_clearance_status': self.police_clearance_status,
            'police_clearance_notes': self.police_clearance_notes,
            'hospital_prep_status': self.hospital_prep_status,
            'hospital_prep_notes': self.hospital_prep_notes,
            'driver_status': self.driver_status,
            'is_simulated': self.is_simulated,
            'accuracy_meters': self.accuracy_meters,
            'last_location_time': self.last_location_time.strftime('%H:%M:%S') if self.last_location_time else None,
            'started_at': self.started_at.strftime('%Y-%m-%d %H:%M:%S') if self.started_at else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None,
            'hospital_ack_status': latest_ack.status if latest_ack else 'pending_ack',
            'hospital_ack_notes': latest_ack.notes if latest_ack else None,
            'triage_priority': latest_ack.triage_priority if latest_ack else 'critical'
        }

class LocationUpdate(db.Model):
    __tablename__ = 'location_updates'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.String(32), db.ForeignKey('emergency_trips.id'), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    speed_kmh = db.Column(db.Float, default=0.0)
    heading = db.Column(db.Float, default=0.0)
    accuracy_meters = db.Column(db.Float, default=5.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_simulated = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed_kmh': self.speed_kmh,
            'heading': self.heading,
            'accuracy_meters': self.accuracy_meters,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_simulated': self.is_simulated
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.String(32), db.ForeignKey('emergency_trips.id'), nullable=False, index=True)
    recipient_type = db.Column(db.String(30), nullable=False) # 'hospital', 'police', 'driver_vicinity', 'admin'
    recipient_id = db.Column(db.String(100), nullable=True)
    channel = db.Column(db.String(30), default='in_app_socket')
    message = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='delivered')
    delivered_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'recipient_type': self.recipient_type,
            'recipient_id': self.recipient_id,
            'channel': self.channel,
            'message': self.message,
            'status': self.status,
            'delivered_at': self.delivered_at.strftime('%H:%M:%S') if self.delivered_at else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class HospitalAcknowledgement(db.Model):
    __tablename__ = 'hospital_acknowledgements'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.String(32), db.ForeignKey('emergency_trips.id'), nullable=False, index=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=False)
    staff_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(30), default='accepted')
    notes = db.Column(db.Text, nullable=True)
    triage_priority = db.Column(db.String(20), default='critical')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    staff = db.relationship('User', foreign_keys=[staff_user_id])

    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'hospital_id': self.hospital_id,
            'staff_name': self.staff.name if self.staff else 'Emergency Desk',
            'status': self.status,
            'notes': self.notes,
            'triage_priority': self.triage_priority,
            'timestamp': self.timestamp.strftime('%H:%M:%S') if self.timestamp else None
        }

class IncidentReport(db.Model):
    __tablename__ = 'incident_reports'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.String(32), db.ForeignKey('emergency_trips.id'), nullable=False, index=True)
    reported_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(30), default='pending_review')
    evidence_notes = db.Column(db.Text, nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewer_action = db.Column(db.String(50), nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
    appeal_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'trip_id': self.trip_id,
            'reported_by': self.reporter.name if self.reporter else 'Anonymous',
            'reason': self.reason,
            'status': self.status,
            'evidence_notes': self.evidence_notes,
            'reviewer_name': self.reviewer.name if self.reviewer else None,
            'reviewer_action': self.reviewer_action,
            'review_notes': self.review_notes,
            'appeal_notes': self.appeal_notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'resolved_at': self.resolved_at.strftime('%Y-%m-%d %H:%M') if self.resolved_at else None
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    target_type = db.Column(db.String(50), nullable=True)
    target_id = db.Column(db.String(100), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    details_json = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', foreign_keys=[user_id])

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user.name if self.user else 'System',
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'ip_address': self.ip_address,
            'details_json': self.details_json,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None
        }
