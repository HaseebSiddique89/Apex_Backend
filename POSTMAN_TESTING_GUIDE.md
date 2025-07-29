# Postman Testing Guide for Apex Backend

This guide provides step-by-step instructions for testing all API endpoints using Postman.

## Setup

1. **Start the Backend Server**
   ```bash
   cd /path/to/Apex_Backend
   python -m backend.app
   ```
   Server will run on `http://127.0.0.1:5000`

2. **Import Environment Variables in Postman**
   Create a new environment in Postman with these variables:
   - `base_url`: `http://127.0.0.1:5000`
   - `auth_token`: (will be set after login)

## Authentication Endpoints

### 1. User Registration
- **Method**: POST
- **URL**: `{{base_url}}/auth/signup`
- **Headers**: 
  - `Content-Type: application/json`
- **Body** (raw JSON):
  ```json
  {
    "email": "test@example.com",
    "password": "your_password"
  }
  ```
- **Expected Response**: 
  ```json
  {
    "message": "Registration initiated. Please check your email to verify your account and complete registration."
  }
  ```

### 2. Email Verification
- **Method**: POST
- **URL**: `{{base_url}}/auth/verify-email`
- **Headers**: 
  - `Content-Type: application/json`
- **Body** (raw JSON):
  ```json
  {
    "email": "test@example.com",
    "token": "verification_token_from_email"
  }
  ```
- **Expected Response**: 
  ```json
  {
    "message": "Email verified successfully. You can now login."
  }
  ```

### 3. User Login
- **Method**: POST
- **URL**: `{{base_url}}/auth/login`
- **Headers**: 
  - `Content-Type: application/json`
- **Body** (raw JSON):
  ```json
  {
    "email": "test@example.com",
    "password": "your_password"
  }
  ```
- **Expected Response**: 
  ```json
  {
    "message": "Login successful",
    "token": "jwt_token_here"
  }
  ```
- **Post-Request Script** (to automatically set auth token):
  ```javascript
  if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set("auth_token", response.token);
  }
  ```

### 4. Resend Verification Email
- **Method**: POST
- **URL**: `{{base_url}}/auth/resend-verification`
- **Headers**: 
  - `Content-Type: application/json`
- **Body** (raw JSON):
  ```json
  {
    "email": "test@example.com"
  }
  ```

## Image Processing Endpoints

### 5. Upload and Process Image (Complete Workflow)
- **Method**: POST
- **URL**: `{{base_url}}/image/upload-complete`
- **Headers**: 
  - `Authorization: Bearer {{auth_token}}`
- **Body** (form-data):
  - `image`: [Select image file]
- **Expected Response**: 
  ```json
  {
    "success": true,
    "message": "Image processing completed successfully. 3D model is being generated separately.",
    "data": {
      "image_id": "image_id_here",
      "image_path": "path/to/image.jpg",
      "isometric_id": "isometric_id_here",
      "isometric_path": "path/to/isometric.png",
      "model3d_id": "model3d_id_here",
      "model3d_task_id": "task_id_here",
      "model3d_status": "pending",
      "model3d_files": null,
      "explanation_id": "explanation_id_here",
      "explanation_path": "path/to/explanation.txt",
      "quiz_id": "quiz_id_here",
      "quiz_path": "path/to/quiz.json",
      "processing_time": "30-60 seconds (3D model generated separately)",
      "processing_status": {
        "isometric": true,
        "explanation": true,
        "quiz": true,
        "model3d": true
      },
      "next_step": "Poll /image/3d/status with model3d_task_id to get GLB file"
    }
  }
  ```

### 6. Check 3D Model Status
- **Method**: POST
- **URL**: `{{base_url}}/image/3d/status`
- **Headers**: 
  - `Authorization: Bearer {{auth_token}}`
  - `Content-Type: application/json`
- **Body** (raw JSON):
  ```json
  {
    "task_id": "task_id_from_upload_response"
  }
  ```
- **Expected Response (Pending)**:
  ```json
  {
    "success": true,
    "data": {
      "status": "processing",
      "local_files": {},
      "model3d_files": null,
      "task_id": "task_id_here",
      "model3d_id": null,
      "message": "3D model status: processing"
    }
  }
  ```
- **Expected Response (Completed)**:
  ```json
  {
    "success": true,
    "data": {
      "status": "completed",
      "local_files": {
        "glb": "3d_models/filename.glb",
        "no_background_image": "no_background_image/filename.png"
      },
      "model3d_files": {
        "glb": "3d_models/filename.glb",
        "no_background_image": "no_background_image/filename.png"
      },
      "task_id": "task_id_here",
      "model3d_id": "model3d_id_here",
      "message": "3D model completed and files downloaded"
    }
  }
  ```

### 7. Get User Images
- **Method**: GET
- **URL**: `{{base_url}}/image/user/images`
- **Headers**: 
  - `Authorization: Bearer {{auth_token}}`
- **Expected Response**: 
  ```json
  {
    "success": true,
    "data": [
      {
        "image_id": "image_id_here",
        "image_path": "path/to/image.jpg",
        "uploaded_at": "2025-07-30T03:07:47.444731692Z",
        "isometric": {
          "isometric_id": "isometric_id_here",
          "isometric_path": "path/to/isometric.png"
        },
        "explanation": {
          "explanation_id": "explanation_id_here",
          "explanation_path": "path/to/explanation.txt"
        },
        "quiz": {
          "quiz_id": "quiz_id_here",
          "quiz_path": "path/to/quiz.json"
        },
        "model3d": {
          "model3d_id": "model3d_id_here",
          "status": "completed",
          "glb_file_path": "3d_models/filename.glb",
          "no_background_path": "no_background_image/filename.png"
        }
      }
    ]
  }
  ```

## Testing Flow

### Complete Workflow Test

1. **Register a new user** using `/auth/signup`
2. **Check your email** for verification link
3. **Verify email** using `/auth/verify-email`
4. **Login** using `/auth/login` (this sets the auth token)
5. **Upload an image** using `/image/upload-complete`
6. **Copy the `model3d_task_id`** from the response
7. **Poll for 3D model status** using `/image/3d/status` with the task_id
8. **Check user images** using `/image/user/images` to see all processed data

### Expected Console Output

When the 3D model completes, you should see:
```
✅ 3D model completed! Downloading files...
🔄 Downloading GLB file from: https://img.theapi.app/temp/...
✅ GLB file saved: 3d_models/filename.glb
🔄 Downloading background image from: https://img.theapi.app/temp/...
✅ Background image saved: no_background_image/filename.png
✅ Database updated for task_id: task_id_here
📁 Files saved: {'glb': '3d_models/filename.glb', 'no_background_image': 'no_background_image/filename.png'}
```

## Database Verification

After successful processing, check your MongoDB `models3d` collection:
```javascript
// The document should be updated with:
{
  "status": "completed",
  "local_files": {
    "glb": "3d_models/filename.glb",
    "no_background_image": "no_background_image/filename.png"
  },
  "completed_at": "2025-07-30T03:10:00.000Z"
}
```

## Troubleshooting

### Common Issues

1. **Authentication Error (401)**
   - Make sure you're logged in and the auth token is set
   - Check if the token is expired

2. **3D Model Status Stays "pending"**
   - This is normal for the first few minutes
   - Continue polling every 15-30 seconds
   - Check console logs for any errors

3. **Database Not Updated**
   - Verify the task_id matches between upload and status calls
   - Check console logs for database update messages

4. **File Download Errors**
   - Check if the upload folder has write permissions
   - Verify the URLs in the PIAPI response are accessible

### Environment Variables

Make sure your `.env` file contains:
```
PIAPI_API_KEY=your_piapi_key_here
GEMINI_API_KEY=your_gemini_key_here
COHERE_API_KEY=your_cohere_key_here
```

## Notes

- The `upload-complete` endpoint processes everything except the 3D model synchronously
- 3D model generation is asynchronous and requires separate polling
- All generated files are saved locally and paths are stored in the database
- The GLB file can be used directly in AR applications
- Database updates use `task_id` for reliable matching 