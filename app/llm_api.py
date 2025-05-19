from flask import Blueprint,json, jsonify, request
from app.intent_parser import parse_intent 
from app.intent_router import IntentRouter
from services.dotnet_api import DotNetAPI
import json

import requests
import re

dotnet_api = DotNetAPI()

llm_api = Blueprint("llm_api", __name__)
router = IntentRouter()

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

Your job is to analyze the user's message and respond in the following JSON format if it's a valid inventory task. 
{{
  "intent": "read_item" | "create_item" | "update_item" | "delete_item",
  "item":   <string> 
}}
There are only four valid types of intent, read_item, create_item, update_item, and delete_item.
User's message:
{user_prompt}
‼️ Reply with ONLY the JSON object – no explanation.

"""
    intent_raw = call_ollama(prompt)

    try:
        intent_data = json.loads(intent_raw)
    except json.JSONDecodeError:
            return {"response": f"Primary prompt: Could not parse JSON: {  intent_raw }"}
     # ── If it isn’t inventory, bail out here (e.g., clarification) ──
    if intent_data.get("intent") != "read_item":
        return {"response": "TEXT: Unsupported or non-inventory request."}
    detail_prompt = f"""
    Respond with a **single JSON object only**.
    • Your reply MUST start with '{{' and end with '}}'.  
    If your first attempt is not valid JSON, output ONLY the valid JSON object on the next line.
    query_type must be either total, by_location, by_lot, expiry, or unknown. If you're not sure pick unknown
     expiry_query must be either earliest, latest,before:<date>,after:<date>, or none
   
    Allowed Keys:
    {{
    "item":          string,                          // required  
    "location":      string,                          // optional  
    "lot_number":    string,                          // optional  
    "expiry_query":  "earliest" | "latest" | "before:<date>" | "after:<date>" | "none",  
    "summary_only":  must be true or false -- lowercase, JSON style                    
    "query_type":    "total" | "by_location" | "by_lot" | "expiry" | "unknown"  
    }}
    
    Example:
    {{
      "item": "biotin",
      "location": "A125",
      "lot_number": "422911R1226",
      "expiry_query":"earliest",
      "summary_only": false,
      "query_type": "total"
    }}

    Item: {intent_data['item']}
    User: {user_prompt}
‼️ **Reply with ONLY the JSON object – no code fences, no commentary.**

    """
    detail_raw = call_ollama(detail_prompt)
    try:
        detail_data = json.loads(detail_raw)       # {"location":"A15", ... } or {}
    except json.JSONDecodeError:
        return {"response": f"TEXT: Could not parse detail JSON: {detail_raw}"}

    # Merge the two dicts
    merged = {**intent_data, **detail_data}        # {"intent":...,"item":...,"location":...}

    # ── STEP C  ──────────────────────────────────────────────
    read_query = parse_intent(merged)              # -> ReadItemQuery dataclass
    if not read_query:
        return {"response": f"Couldn't parse: {merged}"}

    result = router.route(read_query)
      # If there’s a product key and it's an empty list, override the response
    if isinstance(result.get("product"), list) and len(result["product"]) == 0:
        result["response"] = (
            "I’m not seeing any items that match—"
            "could you double-check the item name or try a broader query?"
        )
    return jsonify(result)

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
  return {"response":result.strip()} 

def handle_greeting_prompt():
    return {
        "response": (
            "Hello! I'm Auto Mata, your inventory assistant. "
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
