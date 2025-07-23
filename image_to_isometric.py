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
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY environment variable")
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image '{image_path}' not found")
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/jpeg"
        client = genai.Client(api_key=api_key)
        model = "gemini-2.0-flash-preview-image-generation"
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
        output_dir = "Isometrics"
        os.makedirs(output_dir, exist_ok=True)
        saved_images = set()
        result_files = []
        for chunk in client.models.generate_content_stream(
            model=model, contents=contents, config=config
        ):
            if (chunk.candidates and
                chunk.candidates[0].content and
                chunk.candidates[0].content.parts):
                for part in chunk.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.data:
                        data_hash = hash(part.inline_data.data)
                        if data_hash not in saved_images:
                            try:
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                unique_id = uuid.uuid4().hex[:6]
                                filename = os.path.join(output_dir, f"isometric_{timestamp}_{unique_id}.png")
                                try:
                                    img = Image.open(io.BytesIO(part.inline_data.data))
                                    img.save(filename, "PNG")
                                    result_files.append(filename)
                                except Exception:
                                    try:
                                        decoded_data = base64.b64decode(part.inline_data.data)
                                        img = Image.open(io.BytesIO(decoded_data))
                                        img.save(filename, "PNG")
                                        result_files.append(filename)
                                    except Exception as final_error:
                                        continue
                            except Exception as e:
                                continue
        if not result_files:
            raise RuntimeError("No isometric image generated.")
        # Always return with forward slashes
        return result_files[0].replace("\\", "/")  # Return the first generated file
    except Exception as e:
        raise RuntimeError(f"Error generating isometric image: {e}")
