class Events:
    EVENT_NEW = "EVENT_NEW"
    EVENT_START = "EVENT_START"
    EVENT_ERROR = "EVENT_ERROR"
    EVENT_COMPLETE = "EVENT_COMPLETE"
    EVENT_CANCEL = "EVENT_CANCEL"
    EVENT_DELETE = "EVENT_DELETE"


class States:
    STATE_NEW = "STATE_NEW"
    STATE_RUNNING = "STATE_RUNNING"
    STATE_CANCELING = "STATE_CANCELING"
    STATE_CANCELED = "STATE_CANCELED"
    STATE_ERRORING = "STATE_ERRORING"
    STATE_ERROR = "STATE_ERROR"
    STATE_COMPLETE = "STATE_COMPLETE"
    STATE_DELETED = "STATE_DELETED"


def is_state_done_running(state):
    done_states = [States.STATE_CANCELED,
                   States.STATE_ERROR,
                   States.STATE_COMPLETE,
                   States.STATE_DELETED]
    return state in done_states
