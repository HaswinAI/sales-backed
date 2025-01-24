from flask import Flask
from src.app.routes import app_routes

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(app_routes)

if __name__ == "__main__":
    app.run(debug=True)
