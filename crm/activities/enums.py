from enum import Enum as PyEnum


class ActivityType(str, PyEnum):
    COMMENT = "comment"
    STATUS_CHANGED = "status_changed"
    STAGE_CHANGED = "stage_changed"
    TASK_CREATED = "task_created"
    SYSTEM = "system"

