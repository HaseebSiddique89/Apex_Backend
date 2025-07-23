from quart import Blueprint, request, jsonify, g
import os
from datetime import datetime
from backend.utils.security import login_required
from backend.db.mongo import get_db
from backend.image_processing.utils import (
    async_generate_isometric,
    async_generate_3d,
    async_generate_explanation,
    async_generate_quiz,
    async_get_3d_status
)
import aiohttp

UPLOAD_FOLDER = 'uploads'  # You can change this as needed
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

image_bp = Blueprint('image', __name__, url_prefix='/image')

async def download_and_save_file(url, save_dir, filename=None):
    os.makedirs(save_dir, exist_ok=True)
    if not filename:
        filename = url.split("/")[-1]
    save_path = os.path.join(save_dir, filename)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(save_path, 'wb') as f:
                    f.write(await resp.read())
    return save_path.replace("\\", "/")

@image_bp.route('/upload', methods=['POST'])
@login_required
async def upload_image():
    if 'file' not in (await request.files):
        return jsonify({'error': 'No file part in the request'}), 400
    file = (await request.files)['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save file
    filename = f"{g.current_user['user_id']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    await file.save(filepath)
    filepath = filepath.replace("\\", "/")  # Ensure forward slashes

    # Store metadata in DB
    db = await get_db()
    image_doc = {
        'user_id': g.current_user['user_id'],
        'filename': filename,
        'filepath': filepath,
        'uploaded_at': datetime.utcnow(),
        'status': 'uploaded',
    }
    result = await db.images.insert_one(image_doc)

    # TODO: Trigger processing pipeline (isometric, 3D, etc.)

    return jsonify({'message': 'Image uploaded successfully', 'image_id': str(result.inserted_id)}), 201

@image_bp.route('/isometric', methods=['POST'])
@login_required
async def isometric_api():
    data = await request.get_json()
    image_path = data.get('image_path')
    source_image_id = data.get('source_image_id')
    if not image_path or not os.path.exists(image_path):
        return jsonify({'error': 'Valid image_path required'}), 400
    result = await async_generate_isometric(image_path)
    # Store isometric metadata in DB
    db = await get_db()
    user_id = g.current_user['user_id']
    isometric_doc = {
        'user_id': user_id,
        'filename': os.path.basename(result),
        'filepath': result,
        'uploaded_at': datetime.utcnow(),
        'status': 'generated',
        'type': 'isometric',
    }
    if source_image_id:
        isometric_doc['source_image_id'] = source_image_id
    insert_result = await db.isometrics.insert_one(isometric_doc)
    return jsonify({'result': result, 'isometric_id': str(insert_result.inserted_id)}), 200

@image_bp.route('/3d', methods=['POST'])
@login_required
async def model3d_api():
    data = await request.get_json()
    isometric_path = data.get('isometric_path')
    prompt = data.get('prompt')
    source_isometric_id = data.get('source_isometric_id')
    if not isometric_path or not os.path.exists(isometric_path):
        return jsonify({'error': 'Valid isometric_path required'}), 400
    result = await async_generate_3d(isometric_path, prompt)
    # Store 3D model task metadata in DB (pending, will update on completion)
    db = await get_db()
    user_id = g.current_user['user_id']
    model3d_doc = {
        'user_id': user_id,
        'isometric_path': isometric_path,
        'prompt': prompt,
        'uploaded_at': datetime.utcnow(),
        'status': 'pending',
        'type': '3d_model',
    }
    if source_isometric_id:
        model3d_doc['source_isometric_id'] = source_isometric_id
    insert_result = await db.models3d.insert_one(model3d_doc)
    return jsonify({'result': result, 'model3d_id': str(insert_result.inserted_id)}), 200

@image_bp.route('/3d/status', methods=['POST'])
@login_required
async def model3d_status_api():
    data = await request.get_json()
    task_id = data.get('task_id')
    if not task_id:
        return jsonify({'error': 'task_id is required'}), 400
    result = await async_get_3d_status(task_id)
    # If completed, download and save .glb and image, store in DB
    output = result.get('data', {}).get('output')
    local_files = {}
    if result.get('data', {}).get('status') == 'completed' and output:
        db = await get_db()
        user_id = g.current_user['user_id']
        # Download .glb file
        if 'model_file' in output:
            glb_url = output['model_file']
            glb_path = await download_and_save_file(glb_url, '3d_models')
            model_doc = {
                'user_id': user_id,
                'filename': os.path.basename(glb_path),
                'filepath': glb_path,
                'uploaded_at': datetime.utcnow(),
                'status': 'generated',
                'type': '3d_model',
                'source_task_id': task_id
            }
            await db.images.insert_one(model_doc)
            local_files['glb'] = glb_path
        # Download no_background_image
        if 'no_background_image' in output:
            img_url = output['no_background_image']
            img_path = await download_and_save_file(img_url, 'no_background_image')
            no_bg_doc = {
                'user_id': user_id,
                'filename': os.path.basename(img_path),
                'filepath': img_path,
                'uploaded_at': datetime.utcnow(),
                'status': 'generated',
                'type': 'no_background_image',
                'source_task_id': task_id
            }
            await db.images.insert_one(no_bg_doc)
            local_files['no_background_image'] = img_path
    return jsonify({'result': result, 'local_files': local_files}), 200

@image_bp.route('/explanation', methods=['POST'])
@login_required
async def explanation_api():
    data = await request.get_json()
    image_path = data.get('image_path')
    source_image_id = data.get('source_image_id')
    source_isometric_id = data.get('source_isometric_id')
    if not image_path or not os.path.exists(image_path):
        return jsonify({'error': 'Valid image_path required'}), 400
    result = await async_generate_explanation(image_path)
    # Store description metadata in DB
    db = await get_db()
    user_id = g.current_user['user_id']
    description_doc = {
        'user_id': user_id,
        'filename': os.path.basename(result),
        'filepath': result,
        'uploaded_at': datetime.utcnow(),
        'status': 'generated',
        'type': 'description',
    }
    if source_image_id:
        description_doc['source_image_id'] = source_image_id
    if source_isometric_id:
        description_doc['source_isometric_id'] = source_isometric_id
    insert_result = await db.descriptions.insert_one(description_doc)
    return jsonify({'result': result, 'description_id': str(insert_result.inserted_id)}), 200

@image_bp.route('/quiz', methods=['POST'])
@login_required
async def quiz_api():
    data = await request.get_json()
    description_file_path = data.get('description_file_path')
    num_questions = data.get('num_questions', 3)
    source_description_id = data.get('source_description_id')
    if not description_file_path or not os.path.exists(description_file_path):
        return jsonify({'error': 'Valid description_file_path required'}), 400
    result = await async_generate_quiz(description_file_path, num_questions)
    # Store quiz metadata in DB
    db = await get_db()
    user_id = g.current_user['user_id']
    quiz_doc = {
        'user_id': user_id,
        'filename': os.path.basename(result),
        'filepath': result,
        'uploaded_at': datetime.utcnow(),
        'status': 'generated',
        'type': 'quiz',
    }
    if source_description_id:
        quiz_doc['source_description_id'] = source_description_id
    insert_result = await db.quizzes.insert_one(quiz_doc)
    return jsonify({'result': result, 'quiz_id': str(insert_result.inserted_id)}), 200 