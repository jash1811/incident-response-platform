from dotenv import load_dotenv
from app import create_app
from app.extensions import db
import app.models  # noqa: F401

load_dotenv()

application = create_app()

with application.app_context():
    db.create_all()
    print("Tables created successfully.")

if __name__ == "__main__":
    application.run(
        host="0.0.0.0",
        port=5000,
        debug=application.config.get("DEBUG", False),
    )