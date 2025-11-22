from enum import Enum as PyEnum


class DealStatus(str, PyEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"


class DealStage(str, PyEnum):
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED = "closed"

