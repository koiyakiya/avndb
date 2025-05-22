class VNDBException(Exception):
    """Base class for all VNDB-related exceptions."""
    pass

class IllformedVNDBQuery(VNDBException):
    """Raised when a VNDB query is ill-formed."""
    pass