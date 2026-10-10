import json
from flask import request
from database import db
from models import AuditLog

def log_audit_event(user_id, action, target_type=None, target_id=None, details=None, ip_address=None):
    """
    Writes an immutable security and activity audit entry.
    """
    try:
        if not ip_address and request:
            ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.user_agent.string if request and hasattr(request, 'user_agent') else None
    except Exception:
        if not ip_address:
            ip_address = '127.0.0.1'
        user_agent = 'System Daemon'

    details_str = json.dumps(details) if details and not isinstance(details, str) else details

    log = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        ip_address=ip_address,
        user_agent=user_agent[:250] if user_agent else None,
        details_json=details_str
    )
    db.session.add(log)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
    return log
