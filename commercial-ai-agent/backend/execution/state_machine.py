from enum import Enum
from typing import Optional

class ExecutionState(Enum):
    RECEIVED = "RECEIVED"
    ANALYZING = "ANALYZING"
    PLANNING = "PLANNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    EXECUTING = "EXECUTING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"

class StateMachine:
    def __init__(self, initial_state: ExecutionState = ExecutionState.RECEIVED):
        self.current_state = initial_state
        self.error: Optional[str] = None

    def transition_to(self, new_state: ExecutionState, error: Optional[str] = None):
        """Transition to a new state."""
        # Optional: Add validation rules for state transitions here
        self.current_state = new_state
        if error:
            self.error = error

    def is_terminal(self) -> bool:
        return self.current_state in (ExecutionState.COMPLETED, ExecutionState.FAILED)
