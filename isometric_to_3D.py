import requests
import json
import time
import os
import base64
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
PIAPI_API_KEY = api_key = os.getenv("PIAPI_API_KEY")
PIAPI_BASE_URL = "https://api.piapi.ai/api/v1/task"

# --- Prepare image for API ---
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

# --- Create Trellis task ---
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

    print("Sending request for image-to-3D task...")
    try:
        response = requests.post(PIAPI_BASE_URL, headers=headers, data=json.dumps(payload))
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating task: {e}")
        return None

# --- Get task status ---
def get_trellis_task_status(task_id):
    headers = {
        "x-api-key": PIAPI_API_KEY
    }
    url = f"{PIAPI_BASE_URL}/{task_id}"
    try:
        response = requests.get(url, headers=headers)
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting task status for {task_id}: {e}")
        return None

# --- Main ---
if __name__ == "__main__":
    image_file_path = "D:\\Work\\GitHub\\Trellis_ImageTo3D_Setup\\isometric-house.jpg"
    encoded_img = prepare_image_for_api(image_file_path)

    if encoded_img:
        additional_prompt = "a highly detailed 3D model with realistic textures"
        create_response = create_trellis_image_to_3d_task(encoded_img, prompt=additional_prompt)

        if create_response and create_response.get("code") == 200:
            task_id = create_response["data"]["task_id"]
            print(f"Image-to-3D Task created successfully. Task ID: {task_id}")

            status = "pending"
            while status not in ["completed", "failed"]:
                print(f"Polling for task status... Current status: {status}")
                time.sleep(15)

                task_status_response = get_trellis_task_status(task_id)
                if task_status_response and task_status_response.get("code") == 200:
                    status = task_status_response["data"]["status"]
                    print(f"Updated status: {status}")

                    if status == "completed":
                        result_data = task_status_response["data"].get("output")
                        if result_data:
                            print("\nTask Completed! Generated 3D Model URLs:")
                            for fmt, url in result_data.items():
                                print(f"- {fmt}: {url}")

                            # --- Download GLB file if available ---
                            if "model_file" in result_data:
                                glb_url = result_data["model_file"]
                                
                                # Ensure 'models' folder exists
                                os.makedirs("models", exist_ok=True)
                                
                                file_name = f"models/trellis_model_{task_id}.glb"
                                try:
                                    print(f"Downloading GLB file from: {glb_url}")
                                    glb_response = requests.get(glb_url, stream=True)
                                    glb_response.raise_for_status()
                                    with open(file_name, 'wb') as f:
                                        for chunk in glb_response.iter_content(chunk_size=8192):
                                            f.write(chunk)
                                    print(f"✅ GLB file saved in 'models' folder as: {file_name}")
                                except requests.exceptions.RequestException as e:
                                    print(f"Error downloading GLB file: {e}")
                            else:
                                print("GLB format not found in result. Available formats:", result_data.keys())
                        else:
                            print("Task completed but no result data found.")
                        break

                    elif status == "failed":
                        error_message = task_status_response["data"]["error"]["message"]
                        print(f"❌ Task failed: {error_message}")
                        print("Logs:", task_status_response["data"].get("logs", []))
                        break
                else:
                    print("Failed to retrieve task status.")
                    break
        else:
            print("❌ Failed to create Trellis image-to-3D task.")
    else:
        print("❌ Image preparation failed.")
