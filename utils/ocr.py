import base64
import openai
import re

def extract_vehicle_info(image_path):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that extracts only the vehicle registration number, make, and model as plain values. Respond in this format only:\nRegistration Number: <value>\\nMake: <value>\\nModel: <value>"
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract the vehicle registration number, make, and model from this image:"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )

    text = response.choices[0].message.content
    print("==== GPT OCR RESPONSE ====")
    print(text)
    print("==========================")

    # Match clean key-value lines
    reg = re.search(r"Registration Number[:：]?\s*(.+)", text, re.IGNORECASE)
    make = re.search(r"Make[:：]?\s*(.+)", text, re.IGNORECASE)
    model = re.search(r"Model[:：]?\s*(.+)", text, re.IGNORECASE)

    return (
        reg.group(1).strip() if reg else '',
        make.group(1).strip() if make else '',
        model.group(1).strip() if model else ''
    )
