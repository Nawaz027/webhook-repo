from flask import Flask
from flask_cors import CORS  # Import CORS
from app.webhook.routes import webhook
from app.extensions import mongo  # Import the mongo object

# Creating our flask app
def create_app():
    app = Flask(__name__)

    # Enable CORS for all routes
    CORS(app)  # Add this line to enable CORS

    # Configuring MongoDB URI
    app.config["MONGO_URI"] = "mongodb://localhost:27017/github"
    
    # Initialize MongoDB with the app
    mongo.init_app(app)
    
    # Registering all the blueprints
    app.register_blueprint(webhook)

    return app
