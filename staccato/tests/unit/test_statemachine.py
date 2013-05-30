import testtools

import mox

import staccato.xfer.events as xfer_events
import staccato.xfer.constants as constants


class TestEventsStateMachine(testtools.TestCase):

    def setUp(self):
        super(TestEventsStateMachine, self).setUp()
        self.mox = mox.Mox()

    def tearDown(self):
        super(TestEventsStateMachine, self).tearDown()
        self.mox.UnsetStubs()

    def test_printer(self):
        # just make sure it works
        xfer_events._print_state_machine()

    def test_state_new_to_running(self):
        executor = self.mox.CreateMockAnything()
        db = self.mox.CreateMockAnything()
        xfer_request = self.mox.CreateMockAnything()
        xfer_request.state = constants.States.STATE_NEW
        xfer_request.id = "ID"
        my_states = xfer_events.XferStateMachine(executor)
        self.mox.StubOutWithMock(my_states, 'state_running_handler')
        self.mox.StubOutWithMock(my_states, '_get_current_state')
        self.mox.StubOutWithMock(my_states, '_state_changed')

        my_states._get_current_state(
            db=db,
            xfer_request=xfer_request).AndReturn(constants.States.STATE_NEW)
        my_states._state_changed(constants.States.STATE_NEW,
                                 constants.Events.EVENT_START,
                                 constants.States.STATE_RUNNING,
                                 db=db, xfer_request=xfer_request)

        # the function pointers and mox make the next stub not work
        # my_states.state_running_handler(
        #     constants.States.STATE_NEW,
        #     constants.Events.EVENT_START,
        #     constants.States.STATE_RUNNING,
        #     db,
        #     xfer_request)
        executor.execute(xfer_request.id, my_states)

        self.mox.ReplayAll()
        my_states.event_occurred(constants.Events.EVENT_START,
                                 xfer_request=xfer_request,
                                 db=db)
        self.mox.VerifyAll()
