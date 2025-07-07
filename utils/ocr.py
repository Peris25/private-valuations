import base64
import mimetypes
import openai
import re
from utils.mapping import get_category_and_price
from pdf2image import convert_from_path
import tempfile
import os

def extract_vehicle_info(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type == "application/pdf":
        with tempfile.TemporaryDirectory() as tempdir:
            images = convert_from_path(file_path, output_folder=tempdir, fmt='jpeg')
            image_path = os.path.join(tempdir, "page.jpg")
            images[0].save(image_path, "JPEG")

            with open(image_path, "rb") as file:
                file_data = file.read()
                base64_file = base64.b64encode(file_data).decode("utf-8")
    else:
        with open(file_path, "rb") as file:
            file_data = file.read()
            base64_file = base64.b64encode(file_data).decode("utf-8")

    data_url = f"data:image/jpeg;base64,{base64_file}"

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that extracts only the vehicle registration number, make, model, and body/body type as plain values. Respond in this format only:\\nRegistration Number: <value>\\nMake: <value>\\nModel: <value>\\nBody Type: <value>"
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract vehicle details from this image:"},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]
            }
        ]
    )

    text = response.choices[0].message.content
    print("==== GPT OCR RESPONSE ====")
    print(text)
    print("==========================")

    reg = re.search(r"Registration Number[:：]?\s*(.+)", text, re.IGNORECASE)
    make = re.search(r"Make[:：]?\s*(.+)", text, re.IGNORECASE)
    model = re.search(r"Model[:：]?\s*(.+)", text, re.IGNORECASE)
    body = re.search(r"Body Type[:：]?\s*(.+)", text, re.IGNORECASE)

    registration = reg.group(1).strip() if reg else ''
    make_value = make.group(1).strip() if make else ''
    model_value = model.group(1).strip() if model else ''
    body_type = body.group(1).strip() if body else ''

    category, price = get_category_and_price(body_type)

    return registration, make_value, model_value, body_type, category, price
