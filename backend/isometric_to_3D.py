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
            print(f"Resizing image from {img.size} to fit within {max_size}")
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        encoded_image = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
        
        return encoded_image
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def create_trellis_image_to_3d_task(encoded_image_string, prompt=None):
    if not PIAPI_API_KEY:
        raise RuntimeError("PIAPI_API_KEY not found in environment variables")
    
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
    
    print("🔄 Sending request for image-to-3D task...")
    try:
        response = requests.post(PIAPI_BASE_URL, headers=headers, data=json.dumps(payload), timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Response Text: {response.text}")
        
        response.raise_for_status()
        result = response.json()
        
        # Check if task was created successfully
        if result.get("code") == 200 and result.get("data", {}).get("task_id"):
            task_id = result["data"]["task_id"]
            print(f"✅ Image-to-3D Task created successfully. Task ID: {task_id}")
            return result
        else:
            print(f"❌ Failed to create task. Response: {result}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating task: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def get_trellis_task_status(task_id):
    if not PIAPI_API_KEY:
        raise RuntimeError("PIAPI_API_KEY not found in environment variables")
    
    headers = {
        "x-api-key": PIAPI_API_KEY
    }
    url = f"{PIAPI_BASE_URL}/{task_id}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Response Text: {response.text}")
        
        response.raise_for_status()
        result = response.json()
        
        # Return the full response structure as expected by our code
        return {
            'data': {
                'status': result.get('data', {}).get('status'),
                'output': result.get('data', {}).get('output')
            }
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting task status for {task_id}: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None
