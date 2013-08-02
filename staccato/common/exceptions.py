

class StaccatoBaseException(Exception):
    pass


class StaccatoNotImplementedException(StaccatoBaseException):
    pass


class StaccatoProtocolConnectionException(StaccatoBaseException):
    pass


class StaccatoCancelException(StaccatoBaseException):
    pass


class StaccatoIOException(StaccatoBaseException):
    pass


class StaccatoParameterError(StaccatoBaseException):
    pass


class StaccatoMisconfigurationException(StaccatoBaseException):
    pass


class StaccatoDataBaseException(StaccatoBaseException):
    pass


class StaccatoEventException(StaccatoBaseException):
    pass


class StaccatoInvalidStateTransitionException(StaccatoEventException):
    pass


class StaccatoDatabaseException(StaccatoBaseException):
    pass


class StaccatoNotFoundInDBException(StaccatoDataBaseException):

    def __init__(self, ex, unfound_item):
        super(StaccatoNotFoundInDBException, self).__init__(self, ex)
        self.unfound_item = unfound_item