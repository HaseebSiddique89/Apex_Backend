# Fixed Gemini 2.0 Isometric Image Generator
# pip install google-genai Pillow

import base64
import mimetypes
import os
from google import genai
from google.genai import types
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()

def generate_isometric_image(image_path):
    """Generate isometric view from image with proper error handling"""
   
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    # api_key = "AIzaSyBSFdHtnppuXaWcVCuEV4cTXl7kg5plnsI"
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
                    types.Part.from_text(text="Generate isometric view of this Image"),
                    types.Part.from_bytes(data=image_data, mime_type=mime_type),
                ],
            ),
        ]
       
        config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            response_mime_type="text/plain",
        )
       
        # Generate and save
        print("Generating isometric view...")
        file_index = 0
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
                        # Create a hash to avoid duplicate saves
                        data_hash = hash(part.inline_data.data)
                        if data_hash not in saved_images:
                            try:
                                filename = f"isometric_{file_index}.png"
                                
                                # Try to save directly first
                                try:
                                    img = Image.open(io.BytesIO(part.inline_data.data))
                                    img.save(filename, "PNG")
                                    print(f"Saved: {filename} ({len(part.inline_data.data)} bytes)")
                                except Exception:
                                    # If direct method fails, try base64 decoding
                                    try:
                                        decoded_data = base64.b64decode(part.inline_data.data)
                                        img = Image.open(io.BytesIO(decoded_data))
                                        img.save(filename, "PNG")
                                        print(f"Saved (base64 decoded): {filename} ({len(decoded_data)} bytes)")
                                    except Exception as final_error:
                                        print(f"Error saving image: {final_error}")
                                        continue
                                
                                saved_images.add(data_hash)
                                file_index += 1
                                
                            except Exception as save_error:
                                print(f"Error saving image: {save_error}")
                   
                    # Print text response
                    elif hasattr(part, 'text') and part.text:
                        print(f"Response: {part.text}")
           
            # Also check for text at chunk level
            elif hasattr(chunk, 'text') and chunk.text:
                print(f"Response: {chunk.text}")
   
    except Exception as e:
        print(f"Error: {e}")
        import traceback
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
    image_path = "D:\\Work\\GitHub\\Trellis_ImageTo3D_Setup\\Cell.jpg"
    
    # First verify the input image
    print("Verifying input image...")
    if verify_image(image_path):
        generate_isometric_image(image_path)
        
        # Check generated images
        print("\nVerifying generated images...")
        for i in range(5):  # Check first 5 possible generated images
            for prefix in ["isometric_", "validated_isometric_", "final_isometric_"]:
                filename = f"{prefix}{i}.png"
                if os.path.exists(filename):
                    verify_image(filename)
    else:
        print("Input image is invalid, cannot proceed.")