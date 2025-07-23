
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

from models import db

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")


# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)


# Register Blueprints
from views.valuation import valuation_bp
app.register_blueprint(valuation_bp)

from views.payments import payments_bp
app.register_blueprint(payments_bp)

from views.callback import callback_bp
app.register_blueprint(callback_bp)

from test import test_bp
app.register_blueprint(test_bp)

if __name__ == '__main__':
    app.run(debug=False)

