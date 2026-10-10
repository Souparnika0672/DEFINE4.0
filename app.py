import os
from flask import Flask, render_template
from flask_login import LoginManager
from config import config
from database import db, init_db
from models import User
from sockets import init_sockets, socketio
from seed_data import seed_database

# Blueprints
from auth import auth_bp
from routes.main_routes import main_bp
from routes.user_routes import user_bp
from routes.emergency_routes import emergency_bp
from routes.hospital_routes import hospital_bp
from routes.police_routes import police_bp
from routes.admin_routes import admin_bp
from routes.incident_routes import incident_bp
from routes.api_routes import api_bp

def create_app(config_name=None):
    if config_name is None:
        flask_env = os.environ.get('FLASK_ENV', 'development')
        config_name = 'production' if flask_env == 'production' else flask_env

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # Initialize Database
    init_db(app)

    # Initialize Socket.IO
    init_sockets(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(emergency_bp)
    app.register_blueprint(hospital_bp)
    app.register_blueprint(police_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(incident_bp)
    app.register_blueprint(api_bp)

    # Global Template Context
    @app.context_processor
    def inject_globals():
        return {
            'app_name': app.config.get('APP_NAME', 'EmergencyPass'),
            'app_subtitle': app.config.get('APP_SUBTITLE', 'Smart Emergency Private Vehicle Assistance System'),
            'demo_mode': app.config.get('DEMO_MODE', True)
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_message="Page Not Found (404)"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_message="Internal Server Error (500)"), 500

    # Auto-seed sample database in development
    with app.app_context():
        try:
            if User.query.count() == 0:
                seed_database()
        except Exception as ex:
            print(f"Database initialization notice: {ex}")

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n" + "="*70)
    print(f"  EmergencyPass — Smart Emergency Private Vehicle Assistance System")
    print(f"  Server starting at: http://127.0.0.1:{port}")
    print(f"  Demo Driver:    driver@emergency.org    / DemoUser123!")
    print(f"  Demo Hospital:  hospital@emergency.org  / DemoHospital123!")
    print(f"  Demo Police:    police@emergency.org    / DemoPolice123!")
    print(f"  Demo Admin:     admin@emergency.org     / DemoAdmin123!")
    print(f"="*70 + "\n")
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
