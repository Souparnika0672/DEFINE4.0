from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from database import db
from models import User, Role, Vehicle, Hospital
from services.audit_service import log_audit_event

auth_bp = Blueprint('auth', __name__)

def role_required(*role_names):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            if not current_user.has_role(*role_names):
                flash('Access denied: You do not have permission to access this area.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_user_dashboard(current_user)

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash('Please provide both email and password.', 'warning')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('Your account has been deactivated. Please contact an administrator.', 'danger')
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        log_audit_event(user.id, 'USER_LOGIN', 'user', str(user.id), details={'email': user.email, 'role': user.role.name})
        
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        
        return redirect_user_dashboard(user)

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect_user_dashboard(current_user)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Vehicle details
        reg_number = request.form.get('reg_number', '').strip().upper()
        vehicle_type = request.form.get('vehicle_type', 'Car')
        make_model = request.form.get('make_model', '').strip()
        color = request.form.get('color', '').strip()

        # Validation
        if not name or not email or not password:
            flash('Please complete all required fields.', 'warning')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'warning')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists. Please log in.', 'danger')
            return render_template('auth/register.html')

        if reg_number and Vehicle.query.filter_by(registration_number=reg_number).first():
            flash(f'Vehicle registration number {reg_number} is already registered.', 'danger')
            return render_template('auth/register.html')

        # Public user role
        user_role = Role.query.filter_by(name='user').first()
        if not user_role:
            user_role = Role(name='user', description='Standard public vehicle owner')
            db.session.add(user_role)
            db.session.commit()

        new_user = User(
            name=name,
            email=email,
            phone=phone,
            role_id=user_role.id,
            is_active=True
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        # Register primary vehicle if provided
        if reg_number and make_model and color:
            vehicle = Vehicle(
                user_id=new_user.id,
                registration_number=reg_number,
                vehicle_type=vehicle_type,
                make_model=make_model,
                color=color,
                is_verified=True, # Auto-approved for standard demo onboarding
                verification_status='approved'
            )
            db.session.add(vehicle)

        db.session.commit()
        log_audit_event(new_user.id, 'USER_REGISTERED', 'user', str(new_user.id), details={'email': new_user.email})
        
        login_user(new_user)
        flash('Account registered successfully! Welcome to EmergencyPass.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    log_audit_event(current_user.id, 'USER_LOGOUT', 'user', str(current_user.id))
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('main.index'))

def redirect_user_dashboard(user):
    if user.is_admin:
        return redirect(url_for('admin.dashboard'))
    elif user.is_hospital:
        return redirect(url_for('hospital.dashboard'))
    elif user.is_police:
        return redirect(url_for('police.dashboard'))
    else:
        return redirect(url_for('user.dashboard'))
