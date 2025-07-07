from models import PaymentRequest, db
from flask import Blueprint, request, session
import logging
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

callback_bp = Blueprint('callback', __name__)
SOLVIT_API_URL = "https://login.solvit.limited/api/request/schedule-initiate-request"  

def normalize_phone_for_solvit(phone):
    if phone.startswith("254"):
        return phone[3:]
    return phone

@callback_bp.route('/daraja-callback', methods=['POST'])
def daraja_callback():
    logging.warning("🔥 CALLBACK HIT — HEADERS: %s", dict(request.headers))
    logging.warning("🔥 RAW BODY: %s", request.data)

    try:
        data = request.get_json(force=True)
        logging.warning("✅ CALLBACK ROUTE HIT WITH DATA: %s", data)
    except Exception as e:
        logging.error("❌ Failed to parse JSON: %s", str(e))
        return {"ResultCode": 1, "ResultDesc": "Invalid JSON"}, 400

    stk_callback = data.get("Body", {}).get("stkCallback", {})
    result_code = stk_callback.get("ResultCode")
    checkout_id = stk_callback.get("CheckoutRequestID")

    if not checkout_id:
        logging.error("❌ No CheckoutRequestID found in callback")
        return {"ResultCode": 1, "ResultDesc": "Missing checkout ID"}, 400

    payment = PaymentRequest.query.filter_by(checkout_id=checkout_id).first()

    if payment:
        # Update status
        payment.status = "success" if result_code == 0 else "failed"
        db.session.commit()
        logging.info(f"Payment {checkout_id} marked as {payment.status}")

        # Post to Solvit if payment is successful
        if result_code == 0:
            user_data = {
                "phone": payment.phone,
                "firstName": payment.first_name,
                "lastName": payment.last_name,
                "email": payment.email,
                "reg": payment.reg,
                "latitude": payment.latitude,
                "longitude": payment.longitude
            }
            post_to_solvit(user_data)
        else:
            logging.warning(f"⚠️ Payment failed. ResultCode: {result_code}")

    else:
        logging.warning(f"No matching payment found for checkout_id: {checkout_id}")

    return {"ResultCode": 0, "ResultDesc": "Callback received"}

def get_solvit_token():
    auth_url = os.getenv("SOLVIT_AUTH_URL")
    credentials = {
        "email": os.getenv("SOLVIT_USERNAME"),
        "password": os.getenv("SOLVIT_PASSWORD")
    }
    response = requests.post(auth_url, json=credentials)
    response.raise_for_status()
    return response.json().get("token")

def post_to_solvit(user):
    token = get_solvit_token() 

    payload = {
        "customerMobile": normalize_phone_for_solvit(user.get("phone")),
        "vehicleRegNo": user.get("reg"),
        "firstName": user.get("firstName"),
        "lastName": user.get("lastName"),
        "email": user.get("email"),
        "type": "2",
        "siteType": "2",
        "insuranceCompanyRequestId": "a0T5E000002O1UYUA0",
        "paymentType": "1",
        "isSchedule": "1",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "latitude": user.get("latitude", ""),
        "longitude": user.get("longitude", ""),
        "comment": "Auto-request from Solvit valuation app"
    }
    logging.info("Posting to Solvit API with payload: %s", payload)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{token}"  
    }

    try:
        res = requests.post(SOLVIT_API_URL, json=payload, headers=headers)
        logging.info("Posted to Solvit API: %s", res.json())
    except Exception as e:
        logging.info("Failed to post to Solvit API: %s", str(e))

