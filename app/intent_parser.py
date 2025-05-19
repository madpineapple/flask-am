from app.models import ReadItemQuery, IntentRequest

def parse_intent(data: dict):
    intent = data.get("intent")
    if intent == "read_item":
        rq = ReadItemQuery(
            item=data["item"],
            location=data.get("location"),
            lot_number=data.get("lot_number"),
            expiry_query=data.get("expiry_query"),
            summary_only=data.get("summary_only", False),
            query_type=data.get("query_type")
        )
        return IntentRequest(intent=intent, payload=rq.__dict__)
    # TODO: other intents
    return IntentRequest(intent=intent, payload=data)
