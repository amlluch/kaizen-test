import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Comment:
    id: uuid.UUID
    text: str
    username: str
    post_id: uuid.UUID
    created_at: datetime = field(default_factory=datetime.utcnow)
