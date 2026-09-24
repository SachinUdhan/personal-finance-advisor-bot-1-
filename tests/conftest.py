import pytest
from app import create_app
from config import TestConfig
from models import db, User


@pytest.fixture
def app():
    """Create and configure a fresh app instance for testing with an in-memory database."""
    application = create_app(TestConfig)

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def auth_client(client, app):
    """Test client authenticated with a standard registered test user."""
    with app.app_context():
        user = User(
            full_name="Test Student",
            email="test@example.com",
            age=22,
            monthly_income=50000.0
        )
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

    # Perform login
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'SecurePass123!'
    }, follow_redirects=True)

    return client
