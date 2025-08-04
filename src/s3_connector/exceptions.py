class DataIntegrityError(Exception):
    """
    Raised when the ETag of the downloaded S3 object does not match the
    ETag from the Kafka message, indicating potential data corruption.
    """
    pass
