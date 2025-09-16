from enum import Enum


class OpenaiRunStatus(Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "cancelled"
    CANCELLING = "cancelling"
    INCOMPLETE = "incomplete"
    EXPIRED = "expired"
    REQUIRES_ACTION = "requires_action"
    REQUIRED_ACTION_TYPE = "required_action.type"
