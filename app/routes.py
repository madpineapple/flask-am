from flask import Blueprint, request, jsonify
from app.intent_parser import parse_intent
from app.intent_router import IntentRouter

router = Blueprint("main", __name__)
handler = IntentRouter()


@router.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    intent_req = parse_intent(data)
    result = router.route(intent_req)
    return jsonify(result)
