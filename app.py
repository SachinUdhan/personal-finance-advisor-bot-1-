import os
from flask import Flask, render_template
from config import Config
from models import db
from services.finance_calculator import format_inr


def create_app(config_class=Config):
    """Application factory for Personal Finance Advisor Bot."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database
    db.init_app(app)

    # Register custom Jinja filters
    app.jinja_env.filters['inr'] = format_inr

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.expenses import expenses_bp
    from routes.goals import goals_bp
    from routes.budget import budget_bp
    from routes.calculator import calculator_bp
    from routes.chatbot import chatbot_bp
    from routes.report import report_bp
    from routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(calculator_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(profile_bp)

    # Ensure tables exist
    with app.app_context():
        db.create_all()

    # User-friendly error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_title="404 - Page Not Found", 
                               error_message="The page you requested does not exist or has been relocated."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_title="500 - Internal Server Error", 
                               error_message="An unexpected system error occurred. Please try again shortly."), 500

    return app


app = create_app()

if __name__ == '__main__':
    # Start local development server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=True)
