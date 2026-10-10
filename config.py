import os
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Load environment variables from .env file
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'emergency-pass-secure-prod-key-2026-def-789')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "emergency_pass.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # OpenStreetMap & Routing APIs with API Key Support
    OPENMAP_API_KEY = os.environ.get('OPENMAP_API_KEY', '') # General OpenMaps / Geoapify / LocationIQ key
    OPENROUTESERVICE_API_KEY = os.environ.get('OPENROUTESERVICE_API_KEY', os.environ.get('OPENMAP_API_KEY', ''))
    GEOAPIFY_API_KEY = os.environ.get('GEOAPIFY_API_KEY', os.environ.get('OPENMAP_API_KEY', ''))
    LOCATIONIQ_API_KEY = os.environ.get('LOCATIONIQ_API_KEY', os.environ.get('OPENMAP_API_KEY', ''))
    
    # Base service endpoints
    OSRM_API_URL = os.environ.get('OSRM_API_URL', 'https://router.project-osrm.org')
    OVERPASS_API_URL = os.environ.get('OVERPASS_API_URL', 'https://overpass-api.de/api/interpreter')
    
    # App Settings
    APP_NAME = 'EmergencyPass'
    APP_SUBTITLE = 'Smart Emergency Private Vehicle Assistance System'
    DEMO_MODE = os.environ.get('DEMO_MODE', 'true').lower() in ('true', '1', 't')
    
    # Emergency Proximity alert radius (km)
    VICINITY_ALERT_RADIUS_KM = float(os.environ.get('VICINITY_ALERT_RADIUS_KM', 3.0))
    
    # Location history retention (hours)
    LOCATION_RETENTION_HOURS = int(os.environ.get('LOCATION_RETENTION_HOURS', 24))

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
