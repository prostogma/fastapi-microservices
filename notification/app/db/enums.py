from enum import StrEnum

class PendingStatusEnum(StrEnum):
    pending = "PENDING"
    sent = "SENT"
    failed = "FAILED"