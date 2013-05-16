

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
