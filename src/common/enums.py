from enum import StrEnum, auto


class StrategyStatus(StrEnum):
    NEW = auto()
    TRIGGERED = auto()
    RUNNING = auto()
    STOPPED = auto()
    COMPLETED = auto()
    FAILED = auto()
