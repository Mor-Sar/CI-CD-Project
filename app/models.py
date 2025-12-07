# app/models.py

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class User(db.Model):
    """Users table"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # username – required & unique
    username = db.Column(db.String(80), nullable=False, unique=True)

    # email – required & unique
    email = db.Column(db.String(120), nullable=False, unique=True)

    # password hash
    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # relation to topics (Topic.user_id)
    topics = db.relationship(
        "Topic",
        back_populates="user",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        """Store password as secure hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if plain password matches hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        """JSON-safe representation (no password)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Topic(db.Model):
    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # owner user
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    user = db.relationship("User", back_populates="topics")

    cards = db.relationship(
        "Card",
        back_populates="topic",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user_id": self.user_id,
        }


class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False)

    card_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    topic = db.relationship("Topic", back_populates="cards")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "card_type": self.card_type,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
