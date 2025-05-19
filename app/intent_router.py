# app/intent_router.py
from services.dotnet_api import DotNetAPI
from app.models import ReadItemQuery

class IntentRouter:
    def __init__(self):
        self.api = DotNetAPI()

    def handle_read_item(self, q: ReadItemQuery):
        if q.query_type == "total":
            return {"product": self.api.get_item_total(q.item)}
                  
        if q.query_type == "by_lot":
            return {"product": self.api.get_item_by_lot(q.item, lot_num=q.lot_number)}

        if q.query_type == "by_location":
            return {"product": self.api.get_item_by_loc(q.item, location=q.location)}

        if q.expiry_query:
            return {"product": self.api.get_item_by_expr(q.item, q.expiry_query)}

        # default – full table
        return {"product": self.api.get_item_rows(q.item)}

    def route(self, intent_req):
        intent = intent_req.intent
        if intent == "read_item":
            return self.handle_read_item(ReadItemQuery(**intent_req.payload))
        # future: elif "create_item", ...
        return {"response": f"Unsupported intent: {intent}"}
