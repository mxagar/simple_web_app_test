import pytest
from app import app, db
from models import TextPiece

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    client = app.test_client()

    with app.app_context():
        db.create_all()

    yield client

    with app.app_context():
        db.drop_all()

def test_home_page(client):
    """Test that the home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Submit Text' in response.data  # Assuming 'Submit Text' is part of your home page

def test_submit_text(client):
    """Test submitting a new text piece."""
    response = client.post('/', data={'content': 'Test Content'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Test Content' in response.data

    with app.app_context():
        text_piece = TextPiece.query.first()
        assert text_piece is not None
        assert text_piece.content == 'Test Content'
