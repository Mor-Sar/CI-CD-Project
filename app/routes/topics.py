# app/routes/topics.py

from flask import Blueprint, jsonify, request
from ..models import Topic, Card
from ..services.content_generator import generate_content
from ..constants import VALID_CARD_TYPES
from .. import db
from ..utils.auth_utils import require_user
from ..utils.auth_utils import get_current_user 
from app.services.content_generator import AI_ENABLED


topics_bp = Blueprint("topics", __name__)


@topics_bp.route("/topics", methods=["GET"])
@require_user
def list_topics(current_user):
    topics = Topic.query.filter_by(user_id=current_user.id).all()
    data = [t.to_dict() for t in topics]
    return jsonify(data), 200


@topics_bp.route("/topics", methods=["POST"])
@require_user
def create_topic(current_user):
    """
    Create a new topic and generate cards in the requested formats.
    Expected JSON body:
    {
        "topic": "Docker volumes",
        "formats": ["flashcard", "summary", "quiz"],
        "mode": "dummy" | "ai"
    }
    """
    data = request.get_json()

    if not data or "topic" not in data:
        return jsonify({"error": "Missing 'topic' in request body"}), 400

    topic_name = data["topic"].strip()
    formats = data.get("formats", [])
    mode = data.get("mode", "ai") 
    
    
    if not topic_name:
        return jsonify({"error": "Topic name cannot be empty"}), 400

    if not isinstance(formats, list) or not formats:
        return jsonify({"error": "Formats must be a non-empty list"}), 400

    # validate requested card types
    for f in formats:
        if f not in VALID_CARD_TYPES:
            return jsonify({
                "error": f"Invalid card_type in formats: '{f}'",
                "allowed_types": list(VALID_CARD_TYPES),
            }), 400

    # עכשיו בודקים אם קיים topic עם אותו שם *לאותו משתמש*
    existing = Topic.query.filter_by(
        name=topic_name,
        user_id=current_user.id
    ).first()

    if existing:
        topic = existing
        is_new_topic = False
    else:
        topic = Topic(
            name=topic_name,
            user_id=current_user.id,
    )
        db.session.add(topic)
        db.session.flush()
        is_new_topic = True

    existing_card_types = {
        c.card_type
        for c in Card.query.filter_by(topic_id=topic.id).all()
    }


    created_cards = []
    created_types = []
    skipped_types = []

    for card_type in formats:
        if card_type in existing_card_types:
            skipped_types.append(card_type)
            continue

        content = generate_content(topic.name, card_type, mode=mode)
        card = Card(
            topic_id=topic.id,
            card_type=card_type,
            content=content,
    )
        db.session.add(card)
        created_cards.append(card)
        created_types.append(card_type)

    if not created_cards:
        response = {
        "topic": topic.to_dict(),
        "cards": [],
        "is_new_topic": is_new_topic,
        "created_card_types": [],
        "skipped_card_types": skipped_types,
        "message": "All requested card types already exist for this topic."
    }
        return jsonify(response), 200
    
    db.session.commit()

    response = {
        "topic": topic.to_dict(),
        "cards": [c.to_dict() for c in created_cards],
        "is_new_topic": is_new_topic,
        "created_card_types": created_types,
        "skipped_card_types": skipped_types,
    }
    status_code = 201 if is_new_topic else 200
    return jsonify(response), status_code





@topics_bp.route("/topics/<int:topic_id>/cards", methods=["GET"])
@require_user
def get_topic_cards(current_user, topic_id):
    """
    מחזיר כרטיסים לנושא מסוים של המשתמש המחובר.
    אפשרי query param: ?type=summary לסינון לפי סוג כרטיס.
    """
    topic = Topic.query.filter_by(id=topic_id, user_id=current_user.id).first()
    if topic is None:
        return jsonify({"error": "Topic not found"}), 404

    card_type = request.args.get("type")

    query = Card.query.filter_by(topic_id=topic.id)

    if card_type:
        if card_type not in VALID_CARD_TYPES:
            return jsonify({
                "error": "Invalid card_type",
                "allowed_types": list(VALID_CARD_TYPES),
            }), 400
        query = query.filter_by(card_type=card_type)

    cards = query.all()
    return jsonify([c.to_dict() for c in cards]), 200
