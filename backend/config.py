import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/trellis_db') 