from staccato.common import exceptions


class StateMachine(object):

    def __init__(self):
        # set up the transition table
        self._transitions = {}
        self._state_funcs = {}
        self._state_observer_funcs = {}

    def set_state_func(self, state, func):
        self._state_funcs[state] = func

    def set_state_observer(self, state, func):
        if state not in self._state_observer_funcs:
            self._state_observer_funcs[state] = []
        self._state_observer_funcs[state].append(func)

    def set_mapping(self, state, event, next_state, func=None):
        if state not in self._transitions:
            self._transitions[state] = {}

        event_dict = self._transitions[state]
        if event not in event_dict:
            event_dict[event] = {}

        if func is None:
            func = self._state_funcs[next_state]

        self._transitions[state][event] = (next_state, func)

    def _state_changed(self, current_state, event, new_state, **kwvals):
        raise Exception("this needs to be implemented")

    def _get_current_state(self, **kwvals):
        raise Exception("This needs to be implemented")

    def event_occurred(self, event, **kwvals):

        current_state = self._get_current_state(**kwvals)
        if current_state not in self._transitions:
            raise exceptions.StaccatoInvalidStateTransitionException(
                "Undefined event %s at state %s" % (event, current_state))
        state_ent = self._transitions[current_state]
        if event not in state_ent:
            raise exceptions.StaccatoInvalidStateTransitionException(
                "Undefined event %s at state %s" % (event, current_state))

        next_state, function = state_ent[event]

        self._state_changed(current_state, event, next_state, **kwvals)
        # call all observors.  They are not allowed to effect state change
        for f in self._state_observer_funcs:
            try:
                f(current_state, event, next_state, **kwvals)
            except Exception, ex:
                raise
        # log the change
        if function:
            try:
                function(current_state, event, next_state, **kwvals)
            except Exception, ex:
                # TODO: deal with the exception in a sane way.  we likely need
                # to trigger an event signifying and error occured but we
                # may not want to recurse
                raise

    def mapping_to_digraph(self):
        print 'digraph {'
        for start_state in self._transitions:
            for event in self._transitions[start_state]:
                ent = self._transitions[start_state][event]
                if ent is not None:
                    p_end_state = ent[0].replace("STATE_", '')
                    p_start_state = start_state.replace("STATE_", '')
                    p_event = event.replace("EVENT_", '')
                    print '%s  -> %s [ label = "%s" ];'\
                        % (p_start_state, p_end_state, p_event)
        print '}'
