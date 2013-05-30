"""
This file describes events that can happen on a request structure
"""
from staccato.common import state_machine
from staccato.xfer import constants


class XferStateMachine(state_machine.StateMachine):

    def __init__(self, executor):
        super(XferStateMachine, self).__init__()
        self.map_states()
        self.executor = executor

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

    def state_noop_handler(
            self,
            current_state,
            event,
            new_state,
            db,
            xfer_request,
            **kwvals):
        """
        This handler just allows for the DB change.
        """
        pass

    def state_running_handler(
            self,
            current_state,
            event,
            new_state,
            db,
            xfer_request,
            **kwvals):
        self.executor.execute(xfer_request.id, self)

    def state_delete_handler(
            self,
            current_state,
            event,
            new_state,
            db,
            xfer_request,
            **kwvals):
        db.delete_db_obj(xfer_request)

    def map_states(self):
        self.set_state_func(constants.States.STATE_NEW,
                            self.state_noop_handler)
        self.set_state_func(constants.States.STATE_RUNNING,
                            self.state_running_handler)
        self.set_state_func(constants.States.STATE_CANCELING,
                            self.state_noop_handler)
        self.set_state_func(constants.States.STATE_CANCELED,
                            self.state_noop_handler)
        self.set_state_func(constants.States.STATE_ERRORING,
                            self.state_noop_handler)
        self.set_state_func(constants.States.STATE_ERROR,
                            self.state_noop_handler)
        self.set_state_func(constants.States.STATE_COMPLETE,
                            self.state_noop_handler)
        self.set_state_func(constants.States.STATE_DELETED,
                            self.state_delete_handler)

        # setup the state machine
        self.set_mapping(constants.States.STATE_NEW,
                         constants.Events.EVENT_START,
                         constants.States.STATE_RUNNING)
        self.set_mapping(constants.States.STATE_NEW,
                         constants.Events.EVENT_CANCEL,
                         constants.States.STATE_CANCELED)
        self.set_mapping(constants.States.STATE_NEW,
                         constants.Events.EVENT_DELETE,
                         constants.States.STATE_DELETED)

        self.set_mapping(constants.States.STATE_CANCELED,
                         constants.Events.EVENT_DELETE,
                         constants.States.STATE_DELETED)

        self.set_mapping(constants.States.STATE_CANCELING,
                         constants.Events.EVENT_COMPLETE,
                         constants.States.STATE_COMPLETE)

        self.set_mapping(constants.States.STATE_RUNNING,
                         constants.Events.EVENT_COMPLETE,
                         constants.States.STATE_COMPLETE)
        self.set_mapping(constants.States.STATE_RUNNING,
                         constants.Events.EVENT_CANCEL,
                         constants.States.STATE_CANCELING)
        self.set_mapping(constants.States.STATE_RUNNING,
                         constants.Events.EVENT_ERROR,
                         constants.States.STATE_ERRORING)

        self.set_mapping(constants.States.STATE_ERRORING,
                         constants.Events.EVENT_COMPLETE,
                         constants.States.STATE_ERROR)

        self.set_mapping(constants.States.STATE_COMPLETE,
                         constants.Events.EVENT_DELETE,
                         constants.States.STATE_DELETED)

        self.set_mapping(constants.States.STATE_ERROR,
                         constants.Events.EVENT_START,
                         constants.States.STATE_RUNNING)


def _print_state_machine():
    """
    This function is here to create a state machine diagram of the actual
    code
    """
    my_states = XferStateMachine(None)
    my_states.mapping_to_digraph()
