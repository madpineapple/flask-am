from flask import Blueprint, request, jsonify

main = Blueprint("main", __name__)

@main.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    return jsonify({"response": f"You said: {data.get('prompt')}"})
