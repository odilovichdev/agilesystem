from enum import Enum


class Role(str, Enum):
    admin = "admin"
    owner = "owner"
    developer = "developer"
    manager = "manager"
    tester = "tester"


class Status(str, Enum):
    BACKLOG = "BACKLOG"
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    READY_FOR_TESTING = "READY_FOR_TESTING"
    DONE = "DONE"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class WSEventTypes(str, Enum):
    task_created = "task_created"
    task_status_change = "task_status_change"
    task_move_ready = "task_move_ready"
    task_rejected = "task_rejected"
    task_created_high = "task_created_high"
    task_all = "task_all"



