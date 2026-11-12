"""
User Service - ShopLite
Owner: Maha Al-Tuhfi

Endpoints:
  POST /users        -> register a new user
  POST /login        -> log in, returns a token
  GET  /users/<id>   -> get a user's profile
  GET  /health       -> health check (used by Docker / Kubernetes)
  GET  /metrics      -> metrics for Prometheus (added automatically)
"""
import datetime
import logging
import os

import jwt
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    def to_dict(self):
        # Never return the password hash!
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def create_app(database_url=None):
    app = Flask(__name__)

    # Settings come from environment variables (never hard-code passwords)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or os.getenv(
        "DATABASE_URL", "sqlite:///users.db"
    )
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me-to-32-chars-min")

    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Adds /metrics automatically
    PrometheusMetrics(app)

    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    log = logging.getLogger("user-service")

    @app.get("/health")
    def health():
        return jsonify(status="ok", service="user-service"), 200

    @app.post("/users")
    def register():
        data = request.get_json(silent=True) or {}
        name, email, password = data.get("name"), data.get("email"), data.get("password")

        if not name or not email or not password:
            return jsonify(error="name, email and password are required"), 400
        if User.query.filter_by(email=email).first():
            return jsonify(error="email already registered"), 409

        user = User(name=name, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        log.info("New user registered: id=%s", user.id)
        return jsonify(user.to_dict()), 201

    @app.post("/login")
    def login():
        data = request.get_json(silent=True) or {}
        user = User.query.filter_by(email=data.get("email")).first()

        if not user or not check_password_hash(user.password_hash, data.get("password", "")):
            return jsonify(error="invalid email or password"), 401

        token = jwt.encode(
            {
                "user_id": user.id,
                "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2),
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        log.info("User logged in: id=%s", user.id)
        return jsonify(token=token, user_id=user.id), 200

    @app.get("/users/<int:user_id>")
    def get_user(user_id):
        user = db.session.get(User, user_id)
        if not user:
            return jsonify(error="user not found"), 404
        return jsonify(user.to_dict()), 200

    return app


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    create_app().run(host="0.0.0.0", port=port)