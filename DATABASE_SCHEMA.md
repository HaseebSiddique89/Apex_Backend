# Database Schema Documentation

## 🗄️ **MongoDB Collections with User Relationships**

### **Database:** `Apex_db`

---

## 📊 **Collection Overview**

| Collection | Purpose | User Relationship |
|------------|---------|-------------------|
| `users` | Verified user accounts | Primary user data |
| `pending_users` | Unverified user accounts | Temporary storage |
| `images` | Original uploaded images | `user_id` field |
| `isometrics` | Generated isometric images | `user_id` field |
| `descriptions` | Generated explanations | `user_id` field |
| `quizzes` | Generated quizzes | `user_id` field |
| `models3d` | 3D model metadata | `user_id` field |

---

## 👥 **User Collections**

### **1. `users` Collection**
```json
{
  "_id": ObjectId("..."),
  "username": "testuser",
  "email": "test@example.com",
  "password_hash": "hashed_password",
  "created_at": ISODate("2025-07-28T..."),
  "is_email_verified": true,
  "email_verification_token": null
}
```

### **2. `pending_users` Collection**
```json
{
  "_id": ObjectId("..."),
  "username": "newuser",
  "email": "new@example.com",
  "password_hash": "hashed_password",
  "created_at": ISODate("2025-07-28T..."),
  "is_email_verified": false,
  "email_verification_token": "abc123def456..."
}
```

---

## 📸 **Image Processing Collections**

### **3. `images` Collection**
```json
{
  "_id": ObjectId("..."),
  "user_id": "64f2a1b3c4d5e6f7g8h9i0j1",
  "filename": "user123_20250728_143022_image.jpg",
  "filepath": "uploads/user123_20250728_143022_image.jpg",
  "uploaded_at": ISODate("2025-07-28T14:30:22.123Z"),
  "status": "uploaded"
}
```

### **4. `isometrics` Collection**
```json
{
  "_id": ObjectId("..."),
  "user_id": "64f2a1b3c4d5e6f7g8h9i0j1",
  "filename": "isometric_20250728_143022_abc123.png",
  "filepath": "Isometrics/isometric_20250728_143022_abc123.png",
  "uploaded_at": ISODate("2025-07-28T14:30:25.456Z"),
  "status": "generated",
  "type": "isometric",
  "source_image_id": "64f2a1b3c4d5e6f7g8h9i0j1"
}
```

### **5. `descriptions` Collection**
```json
{
  "_id": ObjectId("..."),
  "user_id": "64f2a1b3c4d5e6f7g8h9i0j1",
  "filename": "image_description_20250728_143022.txt",
  "filepath": "Descriptions/image_description_20250728_143022.txt",
  "uploaded_at": ISODate("2025-07-28T14:30:30.789Z"),
  "status": "generated",
  "type": "description",
  "source_image_id": "64f2a1b3c4d5e6f7g8h9i0j1",
  "source_isometric_id": "64f2a1b3c4d5e6f7g8h9i0j2"
}
```

### **6. `quizzes` Collection**
```json
{
  "_id": ObjectId("..."),
  "user_id": "64f2a1b3c4d5e6f7g8h9i0j1",
  "filename": "image_description_quiz_20250728_143022.json",
  "filepath": "quizzes/image_description_quiz_20250728_143022.json",
  "uploaded_at": ISODate("2025-07-28T14:30:35.123Z"),
  "status": "generated",
  "type": "quiz",
  "source_image_id": "64f2a1b3c4d5e6f7g8h9i0j1",
  "source_description_id": "64f2a1b3c4d5e6f7g8h9i0j4"
}
```

### **7. `models3d` Collection**
```json
{
  "_id": ObjectId("..."),
  "user_id": "64f2a1b3c4d5e6f7g8h9i0j1",
  "isometric_path": "Isometrics/isometric_20250728_143022_abc123.png",
  "uploaded_at": ISODate("2025-07-28T14:30:28.456Z"),
  "status": "completed",
  "type": "3d_model",
  "source_image_id": "64f2a1b3c4d5e6f7g8h9i0j1",
  "source_isometric_id": "64f2a1b3c4d5e6f7g8h9i0j2",
  "task_id": "task_123456789",
  "local_files": {
    "glb": "3d_models/model_20250728_143022.glb",
    "no_background_image": "no_background_image/model_20250728_143022.png"
  }
}
```

---

## 🔗 **Relationships**

### **User → Data Flow:**
```
User (user_id) 
  ↓
  ├── images (user_id)
  │   ↓
  │   ├── isometrics (source_image_id)
  │   │   ↓
  │   │   └── models3d (source_isometric_id)
  │   │
  │   ├── descriptions (source_image_id)
  │   │   ↓
  │   │   └── quizzes (source_description_id)
  │   │
  │   └── models3d (source_image_id)
```

### **Data Relationships:**
- **One-to-One:** User → Image
- **One-to-One:** Image → Isometric
- **One-to-One:** Image → Description
- **One-to-One:** Description → Quiz
- **One-to-One:** Isometric → 3D Model

---

## 🛡️ **Security & Data Isolation**

### **✅ User Data Isolation:**
- All collections include `user_id` field
- Users can only access their own data
- Database queries filter by `user_id`
- No cross-user data leakage

### **✅ Authentication Required:**
- All endpoints require JWT token
- `@login_required` decorator on all routes
- User context available via `g.current_user['user_id']`

---

## 📋 **Database Queries**

### **Get User's Images:**
```javascript
db.images.find({'user_id': 'user_id_here'})
```

### **Get User's Complete Data:**
```javascript
// Get user's images
db.images.find({'user_id': 'user_id_here'})

// Get associated isometrics
db.isometrics.find({'user_id': 'user_id_here'})

// Get associated descriptions
db.descriptions.find({'user_id': 'user_id_here'})

// Get associated quizzes
db.quizzes.find({'user_id': 'user_id_here'})

// Get associated 3D models
db.models3d.find({'user_id': 'user_id_here'})
```

### **Get Complete Processing Chain:**
```javascript
// For a specific image
db.images.findOne({'_id': ObjectId('image_id')})
db.isometrics.findOne({'source_image_id': 'image_id'})
db.descriptions.findOne({'source_image_id': 'image_id'})
db.quizzes.findOne({'source_image_id': 'image_id'})
db.models3d.findOne({'source_image_id': 'image_id'})
```

---

## 🎯 **Key Features**

### **✅ Complete User Isolation:**
- Every record has `user_id`
- Users can only see their own data
- Secure multi-tenant architecture

### **✅ Data Relationships:**
- Clear source relationships
- Easy to trace processing chain
- Maintains data integrity

### **✅ Scalable Design:**
- Indexed on `user_id` for performance
- Separate collections for different data types
- Easy to extend with new features

**All data is properly stored with user_id for complete isolation!** 🛡️ 