# Fixed Gemini 2.0 Isometric Image Generator
# pip install google-genai Pillow

import base64
import mimetypes
import os
import uuid
from datetime import datetime
from google import genai
from google.genai import types
from PIL import Image
import io
import traceback

def generate_isometric_image(image_path):
    """Generate isometric view from image with proper error handling"""

    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: Set GEMINI_API_KEY environment variable")
        return

    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image '{image_path}' not found")
        return

    try:
        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = f.read()

        # Get image type
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/jpeg"

        # Setup client
        client = genai.Client(api_key=api_key)
        model = "gemini-2.0-flash-preview-image-generation"

        # Create request
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="""Generate a rich and detailed isometric view of the object in this image. 
                                                Enhance the perspective to make it visually appealing and 3D-like. Add subtle lighting, shadows, and depth 
                                                to give it a realistic isometric style. Maintain the original features and structure clearly while making it clean and modern. 
                                                This is intended for educational and visual presentation purposes."""),
                    types.Part.from_bytes(data=image_data, mime_type=mime_type),
                ],
            ),
        ]

        config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            response_mime_type="text/plain",
        )

        # Output directory
        output_dir = "Isometrics"
        os.makedirs(output_dir, exist_ok=True)

        print("Generating isometric view...")
        saved_images = set()  # Track saved image hashes to avoid duplicates

        for chunk in client.models.generate_content_stream(
            model=model, contents=contents, config=config
        ):
            if (chunk.candidates and
                chunk.candidates[0].content and
                chunk.candidates[0].content.parts):

                for part in chunk.candidates[0].content.parts:
                    # Save image data with validation
                    if part.inline_data and part.inline_data.data:
                        data_hash = hash(part.inline_data.data)
                        if data_hash not in saved_images:
                            try:
                                # Generate unique filename
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                unique_id = uuid.uuid4().hex[:6]
                                filename = os.path.join(output_dir, f"isometric_{timestamp}_{unique_id}.png")

                                try:
                                    img = Image.open(io.BytesIO(part.inline_data.data))
                                    img.save(filename, "PNG")
                                    print(f"Saved: {filename} ({len(part.inline_data.data)} bytes)")
                                except Exception:
                                    # Try base64 decode if direct fails
                                    try:
                                        decoded_data = base64.b64decode(part.inline_data.data)
                                        img = Image.open(io.BytesIO(decoded_data))
                                        img.save(filename, "PNG")
                                        print(f"Saved (base64 decoded): {filename} ({len(decoded_data)} bytes)")
                                    except Exception as final_error:
                                        print(f"Error saving image: {final_error}")
                                        continue

                                saved_images.add(data_hash)

                            except Exception as save_error:
                                print(f"Error saving image: {save_error}")

                    # Print any text response
                    elif hasattr(part, 'text') and part.text:
                        print(f"Response: {part.text}")

            # Print fallback chunk text
            elif hasattr(chunk, 'text') and chunk.text:
                print(f"Response: {chunk.text}")

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

def verify_image(image_path):
    """Verify if an image can be opened"""
    try:
        with Image.open(image_path) as img:
            print(f"Image {image_path} is valid: {img.format} {img.size} {img.mode}")
            return True
    except Exception as e:
        print(f"Image {image_path} is invalid: {e}")
        return False

if __name__ == "__main__":
    image_path = "D:\\Work\\GitHub\\Trellis_ImageTo3D_Setup\\lungs.jpg"

    # First verify the input image
    print("Verifying input image...")
    if verify_image(image_path):
        generate_isometric_image(image_path)

        # Check generated images in "Isometrics" folder
        print("\nVerifying generated images...")
        output_dir = "Isometrics"
        if os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                if file.endswith(".png"):
                    verify_image(os.path.join(output_dir, file))
    else:
        print("Input image is invalid, cannot proceed.")
