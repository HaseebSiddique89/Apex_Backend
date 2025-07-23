from quart import Quart
from backend.auth import auth_bp
from backend.image_processing import image_bp
from dotenv import load_dotenv
from backend.config import Config

load_dotenv()

app = Quart(__name__)
app.config.from_object(Config)

app.register_blueprint(auth_bp)
app.register_blueprint(image_bp)

@app.route('/')
async def index():
    return {'message': 'Backend is running!'}

if __name__ == '__main__':
    app.run() 