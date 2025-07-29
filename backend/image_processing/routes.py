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
import asyncio

UPLOAD_FOLDER = 'uploads'
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
    """Upload image and automatically generate isometric, 3D model, explanation, and quiz"""
    if 'file' not in (await request.files):
        return jsonify({'error': 'No file provided'}), 400
    
    file = (await request.files)['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save uploaded file
    filename = f"{g.current_user['user_id']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    await file.save(filepath)
    filepath = filepath.replace("\\", "/")

    # Store image metadata in DB
    db = await get_db()
    image_doc = {
        'user_id': g.current_user['user_id'],
        'filename': filename,
        'filepath': filepath,
        'uploaded_at': datetime.utcnow(),
        'status': 'uploaded',
    }
    image_result = await db.images.insert_one(image_doc)
    image_id = str(image_result.inserted_id)

    try:
        # 1. Generate isometric
        isometric_path = await async_generate_isometric(filepath)
        isometric_doc = {
            'user_id': g.current_user['user_id'],
            'filename': os.path.basename(isometric_path),
            'filepath': isometric_path,
            'uploaded_at': datetime.utcnow(),
            'status': 'generated',
            'type': 'isometric',
            'source_image_id': image_id
        }
        isometric_result = await db.isometrics.insert_one(isometric_doc)
        isometric_id = str(isometric_result.inserted_id)

        # 2. Generate 3D model
        model3d_task = await async_generate_3d(isometric_path)
        model3d_doc = {
            'user_id': g.current_user['user_id'],
            'isometric_path': isometric_path,
            'uploaded_at': datetime.utcnow(),
            'status': 'pending',
            'type': '3d_model',
            'source_image_id': image_id,
            'source_isometric_id': isometric_id,
            'task_id': model3d_task.get('task_id') if model3d_task else None
        }
        model3d_result = await db.models3d.insert_one(model3d_doc)
        model3d_id = str(model3d_result.inserted_id)

        # 3. Generate explanation
        explanation_path = await async_generate_explanation(filepath)
        explanation_doc = {
            'user_id': g.current_user['user_id'],
            'filename': os.path.basename(explanation_path),
            'filepath': explanation_path,
            'uploaded_at': datetime.utcnow(),
            'status': 'generated',
            'type': 'description',
            'source_image_id': image_id,
            'source_isometric_id': isometric_id
        }
        explanation_result = await db.descriptions.insert_one(explanation_doc)
        explanation_id = str(explanation_result.inserted_id)

        # 4. Generate quiz
        quiz_path = await async_generate_quiz(explanation_path, 5)
        quiz_doc = {
            'user_id': g.current_user['user_id'],
            'filename': os.path.basename(quiz_path),
            'filepath': quiz_path,
            'uploaded_at': datetime.utcnow(),
            'status': 'generated',
            'type': 'quiz',
            'source_image_id': image_id,
            'source_description_id': explanation_id
        }
        quiz_result = await db.quizzes.insert_one(quiz_doc)
        quiz_id = str(quiz_result.inserted_id)

        return jsonify({
            'success': True,
            'message': 'Image processed successfully',
            'data': {
                'image_id': image_id,
                'image_path': filepath,
                'isometric_id': isometric_id,
                'isometric_path': isometric_path,
                'model3d_id': model3d_id,
                'model3d_task_id': model3d_task.get('task_id') if model3d_task else None,
                'model3d_status': 'pending',
                'model3d_files': None,  # Will be populated when 3D model is ready
                'explanation_id': explanation_id,
                'explanation_path': explanation_path,
                'quiz_id': quiz_id,
                'quiz_path': quiz_path
            }
        }), 201

    except Exception as e:
        # If any step fails, still return the image info
        return jsonify({
            'success': False,
            'message': f'Image uploaded but processing failed: {str(e)}',
            'data': {
                'image_id': image_id,
                'image_path': filepath
            }
        }), 201

@image_bp.route('/upload-complete', methods=['POST'])
@login_required
async def upload_image_complete():
    """Upload image and process everything except 3D model, return task_id for separate polling"""
    if 'file' not in (await request.files):
        return jsonify({'error': 'No file provided'}), 400
    
    file = (await request.files)['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save uploaded file
    filename = f"{g.current_user['user_id']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    await file.save(filepath)
    filepath = filepath.replace("\\", "/")

    # Store image metadata in DB
    db = await get_db()
    image_doc = {
        'user_id': g.current_user['user_id'],
        'filename': filename,
        'filepath': filepath,
        'uploaded_at': datetime.utcnow(),
        'status': 'uploaded',
    }
    image_result = await db.images.insert_one(image_doc)
    image_id = str(image_result.inserted_id)

    # Track what was successful
    successful_processing = {
        'isometric': False,
        'explanation': False,
        'quiz': False,
        'model3d': False
    }

    try:
        # 1. Generate isometric (required for 3D model)
        print(f"🔄 Generating isometric for image: {image_id}")
        isometric_path = await async_generate_isometric(filepath)
        isometric_doc = {
            'user_id': g.current_user['user_id'],
            'filename': os.path.basename(isometric_path),
            'filepath': isometric_path,
            'uploaded_at': datetime.utcnow(),
            'status': 'generated',
            'type': 'isometric',
            'source_image_id': image_id
        }
        isometric_result = await db.isometrics.insert_one(isometric_doc)
        isometric_id = str(isometric_result.inserted_id)
        successful_processing['isometric'] = True
        print(f"✅ Isometric generated: {isometric_path}")

        # 2. Generate explanation
        print(f"🔄 Generating explanation for image: {image_id}")
        explanation_path = await async_generate_explanation(filepath)
        explanation_doc = {
            'user_id': g.current_user['user_id'],
            'filename': os.path.basename(explanation_path),
            'filepath': explanation_path,
            'uploaded_at': datetime.utcnow(),
            'status': 'generated',
            'type': 'description',
            'source_image_id': image_id,
            'source_isometric_id': isometric_id
        }
        explanation_result = await db.descriptions.insert_one(explanation_doc)
        explanation_id = str(explanation_result.inserted_id)
        successful_processing['explanation'] = True
        print(f"✅ Explanation generated: {explanation_path}")

        # 3. Generate quiz (depends on explanation)
        print(f"🔄 Generating quiz for image: {image_id}")
        quiz_path = await async_generate_quiz(explanation_path, 5)
        quiz_doc = {
            'user_id': g.current_user['user_id'],
            'filename': os.path.basename(quiz_path),
            'filepath': quiz_path,
            'uploaded_at': datetime.utcnow(),
            'status': 'generated',
            'type': 'quiz',
            'source_image_id': image_id,
            'source_description_id': explanation_id
        }
        quiz_result = await db.quizzes.insert_one(quiz_doc)
        quiz_id = str(quiz_result.inserted_id)
        successful_processing['quiz'] = True
        print(f"✅ Quiz generated: {quiz_path}")

        # 4. Start 3D model generation (but don't wait for completion)
        print(f"🔄 Starting 3D model generation for image: {image_id}")
        print(f"🔄 Request ID: {id(request)} - User: {g.current_user['user_id']}")
        
        # Check if 3D model already exists for this image
        existing_model3d = await db.models3d.find_one({'source_image_id': image_id})
        if existing_model3d:
            print(f"⚠️ 3D model already exists for image {image_id}, skipping generation")
            model3d_id = str(existing_model3d['_id'])
            task_id = existing_model3d.get('task_id')
            successful_processing['model3d'] = True
        else:
            model3d_task = None
            model3d_id = None
            
            try:
                model3d_task = await async_generate_3d(isometric_path)
                if model3d_task and model3d_task.get("code") == 200:
                    task_id = model3d_task.get("data", {}).get("task_id")
                    if task_id:
                        model3d_doc = {
                            'user_id': g.current_user['user_id'],
                            'isometric_path': isometric_path,
                            'uploaded_at': datetime.utcnow(),
                            'status': 'pending',
                            'type': '3d_model',
                            'source_image_id': image_id,
                            'source_isometric_id': isometric_id,
                            'task_id': task_id
                        }
                        model3d_result = await db.models3d.insert_one(model3d_doc)
                        model3d_id = str(model3d_result.inserted_id)
                        successful_processing['model3d'] = True
                        print(f"✅ 3D model task started: {task_id}")
                    else:
                        print("❌ 3D model task creation failed - no task_id in response")
                else:
                    print("❌ 3D model task creation failed - invalid response")
                    
            except Exception as e:
                print(f"❌ 3D model generation error: {e}")

        # 5. Return all results except GLB file
        return jsonify({
            'success': True,
            'message': 'Image processing completed successfully. 3D model is being generated separately.',
            'data': {
                'image_id': image_id,
                'image_path': filepath,
                'isometric_id': isometric_id,
                'isometric_path': isometric_path,
                'model3d_id': model3d_id,
                'model3d_task_id': task_id,
                'model3d_status': 'pending',
                'model3d_files': None,  # Will be available after polling
                'explanation_id': explanation_id,
                'explanation_path': explanation_path,
                'quiz_id': quiz_id,
                'quiz_path': quiz_path,
                'processing_time': '30-60 seconds (3D model generated separately)',
                'processing_status': successful_processing,
                'next_step': 'Poll /image/3d/status with model3d_task_id to get GLB file'
            }
        }), 201

    except Exception as e:
        print(f"❌ Processing error: {e}")
        # If any step fails, still return the image info
        return jsonify({
            'success': False,
            'message': f'Image uploaded but processing failed: {str(e)}',
            'data': {
                'image_id': image_id,
                'image_path': filepath,
                'processing_status': successful_processing
            }
        }), 201

@image_bp.route('/3d/status', methods=['POST'])
@login_required
async def model3d_status_api():
    """Check 3D model generation status and download GLB file when ready"""
    data = await request.get_json()
    task_id = data.get('task_id')
    model3d_id = data.get('model3d_id')
    
    if not task_id:
        return jsonify({'error': 'task_id is required'}), 400
    
    try:
        print(f"🔄 Checking 3D model status for task: {task_id}")
        result = await async_get_3d_status(task_id)
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'Failed to get task status'
            }), 500
        
        status = result.get('data', {}).get('status')
        output = result.get('data', {}).get('output')
        local_files = {}
        
        print(f"📊 3D model status: {status}")
        
        if status == 'completed' and output:
            print(f"✅ 3D model completed! Downloading files...")
            db = await get_db()
            user_id = g.current_user['user_id']
            
            # Download .glb file
            if 'model_file' in output:
                glb_url = output['model_file']
                print(f"🔄 Downloading GLB file from: {glb_url}")
                glb_path = await download_and_save_file(glb_url, '3d_models')
                local_files['glb'] = glb_path
                print(f"✅ GLB file saved: {glb_path}")
            
            # Download no_background_image
            if 'no_background_image' in output:
                img_url = output['no_background_image']
                print(f"🔄 Downloading background image from: {img_url}")
                img_path = await download_and_save_file(img_url, 'no_background_image')
                local_files['no_background_image'] = img_path
                print(f"✅ Background image saved: {img_path}")
            
            # Update model3d status using task_id (more reliable than model3d_id)
            update_result = await db.models3d.update_one(
                {'task_id': task_id},
                {'$set': {
                    'status': 'completed', 
                    'local_files': local_files,
                    'completed_at': datetime.utcnow()
                }}
            )
            
            if update_result.modified_count > 0:
                print(f"✅ Database updated for task_id: {task_id}")
                print(f"📁 Files saved: {local_files}")
            else:
                print(f"⚠️ Warning: No database record found for task_id: {task_id}")
        
        return jsonify({
            'success': True,
            'data': {
                'status': status,
                'local_files': local_files,
                'model3d_files': local_files if local_files else None,
                'task_id': task_id,
                'model3d_id': model3d_id,
                'message': '3D model completed and files downloaded' if status == 'completed' else f'3D model status: {status}'
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error checking 3D status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@image_bp.route('/user/images', methods=['GET'])
@login_required
async def get_user_images():
    """Get all images and their processing results for the current user"""
    db = await get_db()
    user_id = g.current_user['user_id']
    
    # Get user's images
    images = await db.images.find({'user_id': user_id}).sort('uploaded_at', -1).to_list(length=50)
    
    # Get associated isometrics, explanations, quizzes, and 3D models
    result = []
    for image in images:
        image_id = str(image['_id'])
        
        # Get isometric
        isometric = await db.isometrics.find_one({'source_image_id': image_id})
        
        # Get explanation
        explanation = await db.descriptions.find_one({'source_image_id': image_id})
        
        # Get quiz
        quiz = await db.quizzes.find_one({'source_image_id': image_id})
        
        # Get 3D model
        model3d = await db.models3d.find_one({'source_image_id': image_id})
        
        result.append({
            'image_id': image_id,
            'image_path': image['filepath'],
            'uploaded_at': image['uploaded_at'],
            'isometric': {
                'id': str(isometric['_id']) if isometric else None,
                'path': isometric['filepath'] if isometric else None
            } if isometric else None,
            'explanation': {
                'id': str(explanation['_id']) if explanation else None,
                'path': explanation['filepath'] if explanation else None
            } if explanation else None,
            'quiz': {
                'id': str(quiz['_id']) if quiz else None,
                'path': quiz['filepath'] if quiz else None
            } if quiz else None,
            'model3d': {
                'id': str(model3d['_id']) if model3d else None,
                'task_id': model3d.get('task_id') if model3d else None,
                'status': model3d.get('status') if model3d else None
            } if model3d else None
        })
    
    return jsonify({
        'success': True,
        'data': result
    }), 200 