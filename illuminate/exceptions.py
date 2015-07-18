## Custom Exceptions for InteropDataset

class InteropFileNotFoundError(BaseException):
    def __init__(self, message):
        BaseException.__init__(self, message)

