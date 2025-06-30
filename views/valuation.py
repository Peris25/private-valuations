
import logging
from flask import Blueprint, render_template, request, redirect, session
import os
from utils.ocr import extract_vehicle_info
from utils.mapping import get_category_and_price
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.INFO)

valuation_bp = Blueprint('valuation', __name__, template_folder='../templates')
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@valuation_bp.route('/private', methods=['GET', 'POST'])
def private_upload():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        phone = request.form['phone']
        logbook = request.files['logbook']

        if logbook:
            filename = secure_filename(logbook.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            logbook.save(path)

            reg, make, model = extract_vehicle_info(path)
            category, price = get_category_and_price(make, model)

            session['user'] = {
                'firstName': first_name, 'lastName': last_name,
                'email': email, 'phone': phone,
                'reg': reg, 'make': make, 'model': model,
                'category': category, 'price': price
            }
            return redirect('/preview')

    return render_template("form_upload.html")

@valuation_bp.route('/preview', methods=['GET', 'POST'])
def preview_and_pay():
    if request.method == 'POST':
        for key in session['user']:
            if key in request.form:
                session['user'][key] = request.form[key]
                
        session['user']['latitude'] = request.form.get("latitude")
        session['user']['longitude'] = request.form.get("longitude")
        session.modified = True
        logging.info(f"Location: {session['user'].get('latitude')} , {session['user'].get('longitude')}")

        return redirect('/pay')
    return render_template("preview_and_pay.html", user=session.get('user'))
