import requests
import json
import os
import base64
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

PIAPI_API_KEY = os.getenv("PIAPI_API_KEY")
PIAPI_BASE_URL = "https://api.piapi.ai/api/v1/task"

def prepare_image_for_api(image_path: str, max_size=(1024, 1024)):
    try:
        img = Image.open(image_path)
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        encoded_image = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
        return encoded_image
    except Exception as e:
        raise RuntimeError(f"Error processing image: {e}")

def create_trellis_image_to_3d_task(encoded_image_string, prompt=None):
    headers = {
        "x-api-key": PIAPI_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Qubico/trellis",
        "task_type": "image-to-3d",
        "input": {
            "image": encoded_image_string,
            "ss_sampling_steps": 50,
            "slat_sampling_steps": 50,
            "ss_guidance_strength": 7.5,
            "slat_guidance_strength": 3,
            "seed": 0
        },
        "config": {
            "webhook_config": {
                "endpoint": "",
                "secret": ""
            }
        }
    }
    if prompt:
        payload["input"]["prompt"] = prompt
    try:
        response = requests.post(PIAPI_BASE_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error creating task: {e}")

def get_trellis_task_status(task_id):
    headers = {
        "x-api-key": PIAPI_API_KEY
    }
    url = f"{PIAPI_BASE_URL}/{task_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error getting task status for {task_id}: {e}")
