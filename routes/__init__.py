from functools import wraps
from flask import session, redirect, url_for, flash, g, request
from models import db, User


def login_required(view_func):
    """
    Decorator to protect routes from unauthorized access.
    Redirects to login if user session is absent or invalid.
    """
    @wraps(view_func)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.endpoint))
        
        user = db.session.get(User, user_id)
        if not user:
            session.clear()
            flash("User session expired. Please log in again.", "warning")
            return redirect(url_for('auth.login'))
        
        g.user = user
        return view_func(*args, **kwargs)
    return decorated_function
