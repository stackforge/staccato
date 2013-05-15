"""
This file describes events that can happen on a request structure
"""
from staccato.common import state_machine
from staccato.xfer import constants
from staccato.xfer import executor


class XferStateMachine(state_machine.StateMachine):

    def _state_changed(self, current_state, event, new_state, **kwvals):
        xfer_request = kwvals['xfer_request']
        db = kwvals['db']
        xfer_request.state = new_state
        db.save_db_obj(xfer_request)

    def _get_current_state(self, **kwvals):
        xfer_request = kwvals['xfer_request']
        db = kwvals['db']
        xfer_request = db.lookup_xfer_request_by_id(xfer_request.id)
        return xfer_request.state

g_my_states = XferStateMachine()


def state_noop_handler(
        current_state,
        event,
        new_state,
        conf,
        db,
        xfer_request,
        **kwvals):
    """
    This handler just allows for the DB change.
    """


def state_starting_handler(
        current_state,
        event,
        new_state,
        conf,
        db,
        xfer_request,
        **kwvals):
    g_my_states.event_occurred(constants.Events.EVENT_STARTED,
                               conf=conf,
                               xfer_request=xfer_request,
                               db=db)


def state_running_handler(
        current_state,
        event,
        new_state,
        conf,
        db,
        xfer_request,
        **kwvals):
    executor.SimpleThreadExecutor(xfer_request.id, conf, g_my_states)


def state_delete_handler(
        current_state,
        event,
        new_state,
        conf,
        db,
        xfer_request,
        **kwvals):
    db.delete_db_obj(xfer_request)


g_my_states.set_state_func(constants.States.STATE_NEW,
                           state_noop_handler)
g_my_states.set_state_func(constants.States.STATE_STARTING,
                           state_starting_handler)
g_my_states.set_state_func(constants.States.STATE_RUNNING,
                           state_running_handler)
g_my_states.set_state_func(constants.States.STATE_CANCELING,
                           state_noop_handler)
g_my_states.set_state_func(constants.States.STATE_CANCELED,
                           state_noop_handler)
g_my_states.set_state_func(constants.States.STATE_ERRORING,
                           state_noop_handler)
g_my_states.set_state_func(constants.States.STATE_ERROR,
                           state_noop_handler)
g_my_states.set_state_func(constants.States.STATE_COMPLETE,
                           state_noop_handler)
g_my_states.set_state_func(constants.States.STATE_DELETED,
                           state_delete_handler)

# setup the state machine
g_my_states.set_mapping(constants.States.STATE_NEW,
                        constants.Events.EVENT_START,
                        constants.States.STATE_STARTING)
g_my_states.set_mapping(constants.States.STATE_NEW,
                        constants.Events.EVENT_CANCEL,
                        constants.States.STATE_CANCELED)
g_my_states.set_mapping(constants.States.STATE_NEW,
                        constants.Events.EVENT_START,
                        constants.States.STATE_STARTING)

g_my_states.set_mapping(constants.States.STATE_CANCELED,
                        constants.Events.EVENT_DELETE,
                        constants.States.STATE_DELETED)

g_my_states.set_mapping(constants.States.STATE_STARTING,
                        constants.Events.EVENT_STARTED,
                        constants.States.STATE_RUNNING)
g_my_states.set_mapping(constants.States.STATE_STARTING,
                        constants.Events.EVENT_CANCEL,
                        constants.States.STATE_CANCELING)
g_my_states.set_mapping(constants.States.STATE_STARTING,
                        constants.Events.EVENT_ERROR,
                        constants.States.STATE_ERRORING)

g_my_states.set_mapping(constants.States.STATE_RUNNING,
                        constants.Events.EVENT_COMPLETE,
                        constants.States.STATE_COMPLETE)
g_my_states.set_mapping(constants.States.STATE_RUNNING,
                        constants.Events.EVENT_CANCEL,
                        constants.States.STATE_CANCELING)
g_my_states.set_mapping(constants.States.STATE_RUNNING,
                        constants.Events.EVENT_ERROR,
                        constants.States.STATE_ERRORING)

g_my_states.set_mapping(constants.States.STATE_ERRORING,
                        constants.Events.EVENT_COMPLETE,
                        constants.States.STATE_ERROR)

g_my_states.set_mapping(constants.States.STATE_COMPLETE,
                        constants.Events.EVENT_DELETE,
                        constants.States.STATE_DELETED)

g_my_states.set_mapping(constants.States.STATE_ERROR,
                        constants.Events.EVENT_START,
                        constants.States.STATE_STARTING)


def _print_state_machine():
    g_my_states.mapping_to_digraph()
