from flask import Blueprint, request, jsonify
import requests
import json


llm_api = Blueprint("llm_api", __name__)

OLLAMA_URL = "http://localhost:11434/api/generate"

def call_ollama(prompt: str) -> str:
    response = requests.post(OLLAMA_URL, json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })

    if response.status_code != 200:
        return "ERROR"
    return response.json().get("response", "No response")

# STEP 1: Classify the prompt
def classify_message(user_prompt: str) -> str:
    prompt = f"""
    Classify the following user message into one of the following categories:
    - inventory
    - clarification
    - greeting
    - junk

    Only respond with a single word, no explanation.

    Message: "{user_prompt}"
    """

    result = call_ollama(prompt)
    return result.strip().lower()

# STEP 2: Handle inventory prompts
def handle_inventory_prompt(user_prompt: str):
    prompt = f"""
You are Auto Mata (AM), a warehouse inventory assistant.

Your job is to analyze the user's message and respond ONLY in JSON if it's a valid inventory task. 
Valid intents: `read_item`, `create_item`, `update_item`, `delete_item`.

Return JSON only, prefixed with `JSON:`, like:
JSON: {{
  "intent": "read_item",
  "item": "tapioca starch"
}}

DO NOT include any text outside of the JSON.
Here is the user's message:
{user_prompt}
"""
    response = call_ollama(prompt)
    if response.startswith("JSON:"):
        try:
            return json.loads(response[len("JSON:"):].strip())
        except json.JSONDecodeError:
            return {"response": "TEXT: Failed to parse intent JSON."}
    return {"response": response}

# STEP 2: Handle clarification or greeting
def handle_clarification_prompt(user_prompt: str):
    
  prompt = f"""
    You are Auto Mata (AM), a warehouse inventory assistant.
   Ensure that user understands that he can ask inventory questions or issue inventory commands using plain english. If he is confused give examples of 
   possible commands such as:

   "Check expiration dates for the pork liver"
   "Update the stock levels for the carrot powder"
   "Delete all items with lot number 12345678"
   "Add a new tapioca starch item"
      Here is the user's message:
 "{user_prompt}"

"""
  result = call_ollama(prompt)
  return result.strip().lower()

def handle_greeting_prompt():
    return {
        "response": (
            "TEXT: Hello! I'm Auto Mata, your inventory assistant. "
            "Ask me about stock levels, moving items, or expiring goods. "
            "Example: 'What biotin is closest to expiring?'"
        )
    }
@llm_api.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "")

    category = classify_message(prompt)

    if category == "inventory":
        return handle_inventory_prompt(prompt)
    elif category == "clarification":
        return handle_clarification_prompt(prompt)
    elif category == "greeting":
        return handle_greeting_prompt()
    else:
        return {"response": "TEXT: I’m not sure what you meant. Can you try asking about an item or task in the warehouse?"}
