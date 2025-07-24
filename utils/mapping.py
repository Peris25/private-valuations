# mapping.py

BODY_TYPE_CATEGORY_MAP = {
    "S.WAGON": "Station Wagon",
    "SALOON": "Saloon",
    "HATCHBACK": "Hatchback",
    "SUV": "SUV/4WD",
    "4WD": "SUV/4WD",
    "PICK-UP": "Pick-up",
    "PICKUP": "Pick-up",
    "VAN": "Van",
    "COUPE": "Coupe",
    "BUS": "Bus",
    "MINI BUS": "Mini-bus",
    "MINIBUS": "Mini-bus",
    "TRUCK": "Truck",
    "LORRY": "Truck",
    "TRAILER": "Trailer",
    "MOTOR CYCLE": "Motorcycle",
    "MOTORCYCLE": "Motorcycle"
}

CATEGORY_PRICES = {
    "Saloon": 2500,
    "Hatchback": 2000,
    "Station Wagon": 2500,
    "SUV/4WD": 3000,
    "Pick-up": 2500,
    "Van": 2500,
    "Coupe": 2500,
    "Bus": 3500,
    "Mini-bus": 3000,
    "Truck": 3500,
    "Motorcycle": 1500,
    "Trailer": 3000
}

def get_category_and_price(body_type_raw):
    normalized = body_type_raw.strip().upper()
    category = BODY_TYPE_CATEGORY_MAP.get(normalized, "Saloon")
    price = CATEGORY_PRICES.get(category, 2500)
    return category, price
