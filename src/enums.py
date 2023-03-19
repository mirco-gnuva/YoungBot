from enum import Enum


class StrategyStatus(Enum):
    RUNNING = 'running'
    STOPPED = 'stopped'
    COMPLETED = 'completed'
    FAILED = 'failed'
    NEW = 'new'
    TRIGGERED = 'triggered'
