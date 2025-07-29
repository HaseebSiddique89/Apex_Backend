# Apex Backend

A comprehensive backend for image processing, 3D model generation, and AR content creation.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB (local or Atlas)
- API Keys for:
  - PIAPI.ai (3D model generation)
  - Google Gemini (image processing)
  - Cohere (quiz generation)
  - Gmail SMTP (email verification)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Apex_Backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   MONGODB_URI=your_mongodb_connection_string
   JWT_SECRET_KEY=your_jwt_secret
   PIAPI_API_KEY=your_piapi_key
   GEMINI_API_KEY=your_gemini_key
   COHERE_API_KEY=your_cohere_key
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   EMAIL_FROM=your_email@gmail.com
   EMAIL_FROM_NAME=Apex App
   ```

4. **Run the server**
   ```bash
   python app.py
   ```

The server will start on `http://127.0.0.1:5000`

## 📁 Project Structure

```
Apex_Backend/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── backend/              # Backend package
│   ├── __init__.py
│   ├── app.py           # Internal app configuration
│   ├── config.py        # Configuration settings
│   ├── auth/            # Authentication module
│   ├── image_processing/ # Image processing module
│   ├── db/              # Database utilities
│   ├── models/          # Data models
│   ├── utils/           # Utility functions
│   └── ...
├── docs/                # Documentation
│   ├── POSTMAN_TESTING_GUIDE.md
│   ├── REACT_NATIVE_INTEGRATION_GUIDE.md
│   └── ...
├── tests/               # Test files
├── scripts/             # Utility scripts
├── uploads/             # Uploaded images
├── Isometrics/          # Generated isometric images
├── Descriptions/        # Generated explanations
├── quizzes/             # Generated quizzes
├── 3d_models/          # Generated 3D models
└── no_background_image/ # No-background images
```

## 🔧 API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/verify-email` - Email verification
- `POST /auth/login` - User login
- `POST /auth/resend-verification` - Resend verification email

### Image Processing
- `POST /image/upload-complete` - Upload and process image
- `POST /image/3d/status` - Check 3D model status
- `GET /image/user/images` - Get user's processed images

## 📚 Documentation

- **API Testing**: `docs/POSTMAN_TESTING_GUIDE.md`
- **React Native Integration**: `docs/REACT_NATIVE_INTEGRATION_GUIDE.md`
- **Database Schema**: `docs/DATABASE_SCHEMA.md`
- **Email Setup**: `docs/EMAIL_VERIFICATION_SETUP.md`

## 🧪 Testing

Run tests from the `tests/` directory:
```bash
cd tests
python test_backend.py
```

## 🔍 Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'backend'**
   - Run with: `python app.py` (not `python backend/app.py`)

2. **MongoDB Connection Error**
   - Check your `MONGODB_URI` in `.env`
   - Ensure MongoDB is running

3. **API Key Errors**
   - Verify all API keys are set in `.env`
   - Check API key permissions

4. **Email Verification Issues**
   - Enable 2FA on Gmail
   - Generate App Password
   - Check SMTP settings

## 🚀 Features

- ✅ Email verification system
- ✅ JWT authentication
- ✅ Image upload and processing
- ✅ Isometric image generation
- ✅ 3D model generation (GLB files)
- ✅ Explanation generation
- ✅ Quiz generation
- ✅ AR-ready file formats
- ✅ Database storage with user isolation
- ✅ Asynchronous processing
- ✅ Comprehensive error handling

## 📱 React Native Integration

The backend is optimized for React Native integration with:
- Fast upload endpoints
- Polling for 3D model status
- AR-ready GLB file paths
- Complete user data isolation

See `docs/REACT_NATIVE_INTEGRATION_GUIDE.md` for detailed integration instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Apex Backend** - Powering the future of AR content creation! 🚀✨

