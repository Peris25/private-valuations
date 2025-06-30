
VEHICLE_CATEGORY_MAP = {
    "Toyota Harrier": "SUV",
    "Toyota Premio": "Saloon",
    "Isuzu NQR": "Lorry",
    "TVS HLX": "Motorbike"
}

CATEGORY_PRICES = {
    "SUV": 2500,
    "Saloon": 1,
    "Lorry": 3500,
    "Motorbike": 1500
}

def get_category_and_price(make, model):
    key = f"{make} {model}"
    category = VEHICLE_CATEGORY_MAP.get(key, "Saloon")
    return category, CATEGORY_PRICES[category]
