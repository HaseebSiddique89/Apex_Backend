# Complete API Response Structure

## 🚀 **Optimized Backend API Responses**

### **Base URL:** `http://localhost:5000`

---

## 📤 **API Response Examples**

### **1. Image Upload Response**

**Endpoint:** `POST /image/upload`

**Response:**
```json
{
  "success": true,
  "message": "Image processed successfully",
  "data": {
    "image_id": "64f2a1b3c4d5e6f7g8h9i0j1",
    "image_path": "uploads/user123_20250728_143022_image.jpg",
    "isometric_id": "64f2a1b3c4d5e6f7g8h9i0j2",
    "isometric_path": "Isometrics/isometric_20250728_143022_abc123.png",
    "model3d_id": "64f2a1b3c4d5e6f7g8h9i0j3",
    "model3d_task_id": "task_123456789",
    "model3d_status": "pending",
    "model3d_files": null,
    "explanation_id": "64f2a1b3c4d5e6f7g8h9i0j4",
    "explanation_path": "Descriptions/image_description_20250728_143022.txt",
    "quiz_id": "64f2a1b3c4d5e6f7g8h9i0j5",
    "quiz_path": "quizzes/image_description_quiz_20250728_143022.json"
  }
}
```

### **2. 3D Model Status Response**

**Endpoint:** `POST /image/3d/status`

**Request:**
```json
{
  "task_id": "task_123456789",
  "model3d_id": "64f2a1b3c4d5e6f7g8h9i0j3"
}
```

**Response (Pending):**
```json
{
  "success": true,
  "data": {
    "status": "pending",
    "local_files": {},
    "model3d_files": null
  }
}
```

**Response (Completed):**
```json
{
  "success": true,
  "data": {
    "status": "completed",
    "local_files": {
      "glb": "3d_models/model_20250728_143022.glb",
      "no_background_image": "no_background_image/model_20250728_143022.png"
    },
    "model3d_files": {
      "glb": "3d_models/model_20250728_143022.glb",
      "no_background_image": "no_background_image/model_20250728_143022.png"
    }
  }
}
```

### **3. User Images Response**

**Endpoint:** `GET /image/user/images`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "image_id": "64f2a1b3c4d5e6f7g8h9i0j1",
      "image_path": "uploads/user123_20250728_143022_image.jpg",
      "uploaded_at": "2025-07-28T14:30:22.123Z",
      "isometric": {
        "id": "64f2a1b3c4d5e6f7g8h9i0j2",
        "path": "Isometrics/isometric_20250728_143022_abc123.png"
      },
      "explanation": {
        "id": "64f2a1b3c4d5e6f7g8h9i0j4",
        "path": "Descriptions/image_description_20250728_143022.txt"
      },
      "quiz": {
        "id": "64f2a1b3c4d5e6f7g8h9i0j5",
        "path": "quizzes/image_description_quiz_20250728_143022.json"
      },
      "model3d": {
        "id": "64f2a1b3c4d5e6f7g8h9i0j3",
        "task_id": "task_123456789",
        "status": "completed"
      }
    }
  ]
}
```

---

## 📱 **React Native Integration**

### **1. Upload Image and Get All Results**

```javascript
const uploadImage = async (imageFile, token) => {
  const formData = new FormData();
  formData.append('file', {
    uri: imageFile.uri,
    type: 'image/jpeg',
    name: 'image.jpg',
  });

  const response = await fetch(`${API_BASE_URL}/image/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'multipart/form-data',
    },
    body: formData,
  });
  
  const result = await response.json();
  
  if (result.success) {
    // All processing results are available immediately
    console.log('Image ID:', result.data.image_id);
    console.log('Isometric Path:', result.data.isometric_path);
    console.log('Explanation Path:', result.data.explanation_path);
    console.log('Quiz Path:', result.data.quiz_path);
    console.log('3D Model Status:', result.data.model3d_status);
    console.log('3D Model Task ID:', result.data.model3d_task_id);
  }
  
  return result;
};
```

### **2. Check 3D Model Status**

```javascript
const check3DStatus = async (taskId, model3dId, token) => {
  const response = await fetch(`${API_BASE_URL}/image/3d/status`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ task_id: taskId, model3d_id: model3dId }),
  });
  
  const result = await response.json();
  
  if (result.success && result.data.status === 'completed') {
    // 3D model files are ready for AR view
    console.log('GLB File Path:', result.data.model3d_files.glb);
    console.log('No Background Image:', result.data.model3d_files.no_background_image);
  }
  
  return result;
};
```

### **3. Load 3D Model in AR**

```javascript
const loadARModel = (glbFilePath) => {
  // Use the GLB file path to load in AR view
  return (
    <ARView
      modelPath={glbFilePath}
      modelName="Generated 3D Model"
      enablePlaneDetection={true}
      enableLightEstimation={true}
    />
  );
};
```

---

## 🎯 **Key Features**

### **✅ Immediate Results:**
- Image upload returns all processing results
- Isometric, explanation, and quiz are ready immediately
- Only 3D model takes time (async processing)

### **✅ 3D Model Integration:**
- GLB file path returned when ready
- Direct AR view integration
- Background image also available

### **✅ File Paths:**
- All file paths are server-relative
- Easy to construct full URLs for frontend
- Consistent path structure

### **✅ Error Handling:**
- Partial failures don't break the flow
- Clear status indicators
- Graceful degradation

---

## 🔄 **Complete Workflow**

1. **Upload Image** → Get all results except 3D model
2. **Display Results** → Show isometric, explanation, quiz
3. **Poll 3D Status** → Check every 5 seconds
4. **Load AR View** → Use GLB file path when ready
5. **Interactive Experience** → Full AR + Quiz experience

**Your React Native app now has complete access to all generated content, including AR-ready 3D models!** 🚀 