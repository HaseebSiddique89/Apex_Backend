import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from image_to_isometric import generate_isometric_image
from isometric_to_3D import prepare_image_for_api, create_trellis_image_to_3d_task, get_trellis_task_status
from get_description import generate_description  # Will need to refactor get_description.py
from quiz_generator import generate_quiz  # Will need to refactor quiz_generator.py

async def async_generate_isometric(image_path):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generate_isometric_image, image_path)

async def async_generate_3d(isometric_path, prompt=None):
    loop = asyncio.get_event_loop()
    encoded_img = await loop.run_in_executor(None, prepare_image_for_api, isometric_path)
    if not encoded_img:
        return None
    return await loop.run_in_executor(None, create_trellis_image_to_3d_task, encoded_img, prompt)

async def async_generate_explanation(image_path):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generate_description, image_path)

async def async_generate_quiz(description_file_path, num_questions=3):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generate_quiz, description_file_path, num_questions)

async def async_get_3d_status(task_id):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_trellis_task_status, task_id) 