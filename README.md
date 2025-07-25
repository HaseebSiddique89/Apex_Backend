# Apex Backend – Student Learning App

## Project Overview

This backend powers a student learning app where users can:
- Upload images (e.g., diagrams, textbook images)
- Generate isometric projections and 3D models from images
- Generate explanations/notes for images
- Generate quizzes based on explanations
- Securely authenticate and manage user sessions

---

## Features

- **User Authentication**: Signup, login, JWT-based session management, protected routes.
- **Image Upload**: Authenticated users can upload images.
- **Isometric Generation**: Convert uploaded images to isometric projections.
- **3D Model Generation**: Generate 3D models from isometric images.
- **Explanation/Notes Generation**: Generate textual explanations for images.
- **Quiz Generation**: Create quizzes based on generated explanations.
- **MongoDB Integration**: Store user, image, isometric, description, and quiz metadata.

---

## Packages Used

From `backend/requirements.txt`:

- **quart**: Async web framework (like Flask, but async)
- **motor**: Async MongoDB driver
- **PyJWT**: JWT encoding/decoding for authentication
- **passlib**: Password hashing
- **python-dotenv**: Load environment variables from `.env` files

---

## API Endpoints

### Authentication (`/auth`)

| Endpoint         | Method | Auth Required | Description                |
|------------------|--------|---------------|----------------------------|
| `/auth/signup`   | POST   | No            | Register a new user        |
| `/auth/login`    | POST   | No            | Login and get JWT token    |
| `/auth/protected`| GET    | Yes           | Test protected route       |

#### Example: Signup

- **POST** `/auth/signup`
- **Body** (JSON):
  ```json
  {
    "username": "student1",
    "email": "student1@example.com",
    "password": "yourpassword"
  }
  ```
- **Response**: `201 Created` or error

#### Example: Login

- **POST** `/auth/login`
- **Body** (JSON):
  ```json
  {
    "username_or_email": "student1",
    "password": "yourpassword"
  }
  ```
- **Response**: `{ "access_token": "<JWT>" }`

#### Example: Protected

- **GET** `/auth/protected`
- **Header**: `Authorization: Bearer <JWT>`
- **Response**: `{ "message": "Hello, <username>! This is a protected route." }`

---

### Image Processing (`/image`)

| Endpoint             | Method | Auth Required | Description                        |
|----------------------|--------|---------------|------------------------------------|
| `/image/upload`      | POST   | Yes           | Upload an image                    |
| `/image/isometric`   | POST   | Yes           | Generate isometric from image      |
| `/image/explanation` | POST   | Yes           | Generate explanation from image    |
| `/image/quiz`        | POST   | Yes           | Generate quiz from explanation     |

#### Example: Upload Image

- **POST** `/image/upload`
- **Header**: `Authorization: Bearer <JWT>`
- **Body**: `form-data` with key `file` (the image file)
- **Response**: `{ "message": "Image uploaded successfully", "image_id": "<id>" }`

#### Example: Generate Isometric

- **POST** `/image/isometric`
- **Header**: `Authorization: Bearer <JWT>`
- **Body** (JSON):
  ```json
  {
    "image_path": "uploads/your_image.jpg",
    "source_image_id": "<image_id>"
  }
  ```
- **Response**: `{ "result": "<isometric_path>", "isometric_id": "<id>" }`

#### Example: Generate Explanation

- **POST** `/image/explanation`
- **Header**: `Authorization: Bearer <JWT>`
- **Body** (JSON):
  ```json
  {
    "image_path": "uploads/your_image.jpg",
    "source_image_id": "<image_id>",
    "source_isometric_id": "<isometric_id>"
  }
  ```
- **Response**: `{ "result": "<description_path>", "description_id": "<id>" }`

#### Example: Generate Quiz

- **POST** `/image/quiz`
- **Header**: `Authorization: Bearer <JWT>`
- **Body** (JSON):
  ```json
  {
    "description_file_path": "Descriptions/your_description.txt",
    "num_questions": 3,
    "source_description_id": "<description_id>"
  }
  ```
- **Response**: `{ "result": "<quiz_path>", "quiz_id": "<id>" }`

---

### Explanation and Quiz Blueprints

- Currently, `backend/explanation/routes.py` and `backend/quiz/routes.py` are placeholders and do not expose any endpoints directly. All explanation and quiz generation is handled via `/image/explanation` and `/image/quiz`.

---

## Authentication

- Uses JWT tokens for stateless authentication.
- Passwords are hashed using bcrypt via passlib.
- Use the `Authorization: Bearer <JWT>` header for all protected endpoints.

---

## Database

- Uses MongoDB (async via Motor).
- Collections: `users`, `images`, `isometrics`, `descriptions`, `quizzes`.
- Connection string is set via the `MONGODB_URI` environment variable.

---

## Configuration

- Set environment variables in a `.env` file or system environment:
  - `SECRET_KEY`: Secret for JWT and password hashing
  - `MONGODB_URI`: MongoDB connection string (default: `mongodb://localhost:27017/trellis_db`)
  - `GEMINI_API_KEY`: Gemini API Key
  - `PIAPI_API_KEY`: PIAPI API Key
  - `COHERE_API_KEY`: Cohere API Key

---

## How to Run and Test the Project

### Running the Backend

1. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Set up your `.env` file in the `backend/` directory:
   ```env
   SECRET_KEY=your-secret-key
   MONGODB_URI=mongodb://localhost:27017/trellis_db
   ```
3. Start MongoDB server.
4. Run the backend:
   ```bash
   python backend/app.py
   ```

### Testing with Postman

- **Signup/Login**: Use `/auth/signup` and `/auth/login` to get a JWT.
- **Set JWT**: For all protected endpoints, add a header:
  ```
  Authorization: Bearer <your_jwt_token>
  ```
- **Image Upload**: Use `form-data` with a file field.
- **Other endpoints**: Use JSON bodies as shown above.

---

## File/Folder Structure Overview

```
backend/
  app.py                # Main app entry, registers blueprints
  auth/                 # Authentication logic and routes
  image_processing/     # Image, isometric, explanation, and quiz processing
  models/               # Data models (user, image, quiz, etc.)
  db/                   # Database connection logic
  utils/                # Utility functions (security, file ops)
  requirements.txt      # Python dependencies
uploads/                # Uploaded images
Isometrics/             # Generated isometric images
Descriptions/           # Generated explanations/notes
quizzes/                # Generated quizzes
3d_models/              # Generated 3D models
```

---

## Credits

Developed for educational purposes. Contributions welcome!

