import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from kaizen_blog_api.errors import ValidationError


@dataclass
class Image:
    id: uuid.UUID
    url: str


@dataclass
class Post:
    id: uuid.UUID
    text: str
    username: str
    image: Optional[Image] = None
    likes: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.image and self.image.id != self.id:
            raise ValidationError("Image and post should have same ID")
