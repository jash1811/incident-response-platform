import os
import pymysql
from dotenv import load_dotenv
from app import create_app
from app.extensions import db
import app.models  # noqa: F401 — registers all models with SQLAlchemy

load_dotenv()


def ensure_database_exists():
    """
    Create the MySQL database if it doesn't exist yet.
    Runs before SQLAlchemy tries to connect, so db.create_all() never
    hits 'Unknown database'.
    """
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "incident_platform")

    conn = pymysql.connect(host=host, port=port, user=user, password=password)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
        print(f"Database '{db_name}' is ready.")
    finally:
        conn.close()


if __name__ == "__main__":
    ensure_database_exists()

    application = create_app()

    with application.app_context():
        db.create_all()
        print("Tables created.")

    application.run(
        host="0.0.0.0",
        port=5000,
        debug=application.config.get("DEBUG", False),
    )
