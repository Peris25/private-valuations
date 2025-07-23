from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean

db = SQLAlchemy()

class PaymentRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    checkout_id = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.String, nullable=False)
    stk_phone = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String)
    reg = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    status = db.Column(db.String, default="pending")
    sent_to_solvit = db.Column(db.Boolean, default=False)  # NEW
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)  # NEW