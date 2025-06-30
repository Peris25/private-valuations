from sqlalchemy import text
from flask import Blueprint
from models import db  # change to your actual import

test_bp = Blueprint('test', __name__)

@test_bp.route('/test-db')
def test_db_connection():
    try:
        db.session.execute(text('SELECT 1'))
        return "✅ Database connected successfully."
    except Exception as e:
        return f"❌ Database connection failed: {str(e)}"

