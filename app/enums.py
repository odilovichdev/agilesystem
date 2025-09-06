from enum import Enum


class Role(str, Enum):
    admin = "admin"
    owner = 'owner'
    developer = 'developer'
    manager = 'manager'
    tester = 'tester'


class Status(str, Enum):
    BACKLOG = 'BACKLOG'
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    READY_FOR_TESTING = "READY_FOR_TESTING"
    DONE = "DONE"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"