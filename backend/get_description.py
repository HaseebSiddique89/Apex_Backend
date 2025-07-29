import google.generativeai as genai
from PIL import Image
import os
import io
import mimetypes
import datetime

def generate_description(image_path):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    DESCRIPTIONS_FOLDER = "Descriptions"
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found at {image_path}")
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/jpeg"
        prompt = """You are an educational assistant for students.\n\nGiven the image below, do the following:\n1. Identify the object present in the image.\n2. Describe what it is.\n3. Explain its structure in detail.\n4. Explain its main functions.\n5. Provide any additional relevant information.\n\nDo not include any additional phrases such as \"Here's a breakdown\" or anything else outside of the 5 numbered responses. You may use bullets within these 5 numbered responses for better explanation.\nBe detailed and educational, using clear language suitable for high school and undergraduate students. response must be stick to these 5 points mentioned above, no extra text"""
        contents = [
            {
                'mime_type': mime_type,
                'data': image_data
            },
            prompt
        ]
        response = model.generate_content(contents)
        generated_text = response.text
        os.makedirs(DESCRIPTIONS_FOLDER, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        image_base_name = os.path.splitext(os.path.basename(image_path))[0]
        unique_filename = f"{image_base_name}_description_{timestamp}.txt"
        file_path = os.path.join(DESCRIPTIONS_FOLDER, unique_filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(generated_text)
        return file_path.replace("\\", "/")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}")