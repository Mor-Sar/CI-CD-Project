# app/routes/cards.py

from flask import Blueprint, jsonify, request
from ..models import Card, Topic
from ..constants import VALID_CARD_TYPES
from .. import db
from ..utils.auth_utils import require_user

cards_bp = Blueprint("cards", __name__)


@cards_bp.route("/cards", methods=["GET"])
@require_user
def get_cards(current_user):
    """
    Get all cards for the current user.
    Optional: ?type=summary to filter by card_type.
    """
    card_type = request.args.get("type")

    # מסננים רק כרטיסים של המשתמש הנוכחי דרך Topic
    query = (
        Card.query
        .join(Topic, Card.topic_id == Topic.id)
        .filter(Topic.user_id == current_user.id)
    )

    if card_type:
        if card_type not in VALID_CARD_TYPES:
            return jsonify({
                "error": "Invalid card_type",
                "allowed_types": list(VALID_CARD_TYPES),
            }), 400
        query = query.filter(Card.card_type == card_type)

    cards = query.all()
    return jsonify([c.to_dict() for c in cards]), 200


@cards_bp.route("/cards/<int:card_id>", methods=["PUT"])
@require_user
def update_card(current_user, card_id):
    """
    Update an existing card (card_type and/or content), only if it belongs
    to the current user.
    """
    card = (
        Card.query
        .join(Topic, Card.topic_id == Topic.id)
        .filter(Card.id == card_id, Topic.user_id == current_user.id)
        .first()
    )
    if card is None:
        return jsonify({"error": "Card not found"}), 404

    data = request.get_json(silent=True) or {}

    new_card_type = data.get("card_type")
    new_content = data.get("content")

    if new_card_type is not None:
        if new_card_type not in VALID_CARD_TYPES:
            return jsonify({
                "error": "Invalid card_type",
                "allowed_types": list(VALID_CARD_TYPES),
            }), 400
        card.card_type = new_card_type

    if new_content is not None:
        card.content = new_content

    db.session.commit()

    return jsonify(card.to_dict()), 200


@cards_bp.route("/cards/<int:card_id>", methods=["DELETE"])
@require_user
def delete_card(current_user, card_id):
    """
    Delete a card by ID, only if it belongs to the current user.
    """
    card = (
        Card.query
        .join(Topic, Card.topic_id == Topic.id)
        .filter(Card.id == card_id, Topic.user_id == current_user.id)
        .first()
    )
    if card is None:
        return jsonify({"error": "Card not found"}), 404

    db.session.delete(card)
    db.session.commit()

    return jsonify({"status": "deleted", "id": card_id}), 200
