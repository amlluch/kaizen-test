import json
from dataclasses import asdict, dataclass
from enum import Enum

from kaizen_blog_api.comment.entities import Comment
from kaizen_blog_api.serializers import JSONEncoder, dict_factory


@dataclass
class Event:
    id: str
    name: str
    payload: str


class EventName(Enum):
    COMMENT_CREATED = "comment.created"
    COMMENT_DELETED = "comment.deleted"

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class CommentDeletedEvent(Event):
    def __init__(self, comment: Comment):
        super().__init__(
            str(comment.id),
            str(EventName.COMMENT_DELETED),
            json.dumps(asdict(comment, dict_factory=dict_factory), cls=JSONEncoder),
        )
