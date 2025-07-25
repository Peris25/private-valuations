from models import PaymentRequest, db
from flask import Blueprint, flash, session, redirect, render_template, request, jsonify
import requests
from datetime import datetime
import base64
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

payments_bp = Blueprint('payments', __name__, template_folder='../templates')

# Load Daraja credentials from environment
CONSUMER_KEY = os.getenv("DARJA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("DARJA_CONSUMER_SECRET")
SHORTCODE = os.getenv("DARJA_SHORTCODE")
PASSKEY = os.getenv("DARJA_PASSKEY")
CALLBACK_URL = os.getenv("CALLBACK_URL")

def get_token():
    res = requests.get(
        "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
        auth=(CONSUMER_KEY, CONSUMER_SECRET)
    )
    return res.json().get("access_token")

def initiate_stk(phone, amount):
    token = get_token()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{SHORTCODE}{PASSKEY}{timestamp}".encode()).decode()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    logging.info("Initiating STK Push for phone: %s, amount: %s", phone, amount)
    logging.info(f"CALLBACK_URL from ENV: {os.getenv('CALLBACK_URL')}")

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "PrivateValuation",
        "TransactionDesc": "Vehicle Valuation"
    }

    r = requests.post("https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
    logging.info("STK PUSH RESPONSE: %s", r.json())
    return r.json()

@payments_bp.route('/pay', methods=['GET', 'POST'])
def pay():
    session.modified = True  # Ensure latest session data is used
    user = dict(session.get("user", {}))  # Force copy to avoid mutability weirdness

    logging.info(f"[PAY] Loaded user from session: lat={user.get('latitude')} lng={user.get('longitude')}")

    phone = session.get("payment_phone") 
    logging.info(f"[PAY] Payment phone: {phone}")
    amount = user.get("price")
    body_type = user.get('bodyType')

    response = initiate_stk(phone, amount)
    checkout_id = response.get("CheckoutRequestID")

    if response.get("ResponseCode") == "0" and checkout_id:
        # Save to database if not already recorded
        existing = PaymentRequest.query.filter_by(checkout_id=checkout_id).first()

        if not existing:
            latitude = float(user.get("latitude")) if user.get("latitude") else None
            longitude = float(user.get("longitude")) if user.get("longitude") else None
            
            payment = PaymentRequest(
                checkout_id=checkout_id,
                phone=user.get("phone"),
                stk_phone=phone,
                first_name=user.get("firstName"),
                last_name=user.get("lastName"),
                email=user.get("email"),
                reg=user.get("reg"),
                latitude=latitude,
                longitude=longitude,
                status="pending"
            )
            db.session.add(payment)
            db.session.commit()
            logging.info(f"[DB INSERT] lat: {user.get('latitude')}, lng: {user.get('longitude')}")

        # Save checkout_id to session for polling
        session['payment_status'] = 'pending'
        session['checkout_id'] = checkout_id

        return render_template("payment_pending.html", user=user)
    else:
        session['payment_status'] = 'failed'
        flash("Payment failed. Please try again.")
        return redirect('/confirm-payment')



@payments_bp.route('/success', methods=['GET'])
def payment_success():
    checkout_id = session.get("checkout_id")
    if not checkout_id:
        return redirect('/preview')

    payment = PaymentRequest.query.filter_by(checkout_id=checkout_id).first()
    if not payment or payment.status != 'success':
        return redirect('/preview')

    return render_template("payment_success.html", user=session.get('user'))

@payments_bp.route('/payment-status', methods=['GET'])
def payment_status():
    checkout_id = session.get("checkout_id")
    if not checkout_id:
        return jsonify({"status": "unknown"})

    payment = PaymentRequest.query.filter_by(checkout_id=checkout_id).first()
    if not payment:
        return jsonify({"status": "unknown"})

    return jsonify({"status": payment.status})