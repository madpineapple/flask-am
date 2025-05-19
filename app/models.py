from dataclasses import dataclass
from typing import Optional

@dataclass
class ReadItemQuery:
    item: str
    location: Optional[str] = None
    lot_number: Optional[str] = None
    expiry_query: Optional[str] = None   
    summary_only: bool = False
    query_type:Optional[str] = None


@dataclass
class IntentRequest:
    intent: str               
    payload: dict      
