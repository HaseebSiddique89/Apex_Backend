import google.generativeai as genai
from PIL import Image
import os
import io
import mimetypes
import datetime # Import for generating unique timestamps

# Configure the API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit()

genai.configure(api_key=api_key)

# Define the model
model = genai.GenerativeModel("gemini-2.0-flash") # Using Gemini 2.0 Flash as per your request

# Use a local image path
local_image_path = "D:\\Work\\GitHub\\Trellis_ImageTo3D_Setup\\heart.jpg" # Replace with your actual local path

# --- New: Define the descriptions folder ---
DESCRIPTIONS_FOLDER = "Descriptions"

# Check if the file exists
if not os.path.exists(local_image_path):
    print(f"Error: Image file not found at {local_image_path}")
else:
    try:
        # Read the image file in binary mode
        with open(local_image_path, "rb") as f:
            image_data = f.read()

        # Determine the MIME type
        mime_type, _ = mimetypes.guess_type(local_image_path)
        if not mime_type:
            mime_type = "image/jpeg" # Default if guess_type fails

        prompt = """You are an educational assistant for students.

                    Given the image below, do the following:
                    1. Identify the object present in the image.
                    2. Describe what it is.
                    3. Explain its structure in detail.
                    4. Explain its main functions.
                    5. Provide any additional relevant information (like its role in the human body, diseases related to it, or interesting facts).

                    Be detailed and educational, using clear language suitable for high school and undergraduate students. response must be stick to these 5 points mentioned above, no extra text"""

        contents = [
            {
                'mime_type': mime_type,
                'data': image_data
            },
            prompt
        ]

        print(f"Using model: {model.model_name}")
        print("Generating description...")
        response = model.generate_content(contents)

        generated_text = response.text
        print("\n--- Generated Description ---")
        print(generated_text)
        print("-----------------------------\n")

        # --- New: Save the description to a unique file ---

        # 1. Create the Descriptions folder if it doesn't exist
        os.makedirs(DESCRIPTIONS_FOLDER, exist_ok=True) # exist_ok=True prevents error if folder already exists

        # 2. Generate a unique filename
        # You can use the current timestamp (year-month-day_hour-minute-second)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # Extract base name of the image for better file naming
        image_base_name = os.path.splitext(os.path.basename(local_image_path))[0]
        unique_filename = f"{image_base_name}_description_{timestamp}.txt"
        file_path = os.path.join(DESCRIPTIONS_FOLDER, unique_filename)

        # 3. Save the text to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(generated_text)

        print(f"Description saved to: {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")