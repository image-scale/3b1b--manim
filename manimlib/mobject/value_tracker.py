"""Value tracker mobjects."""


class ValueTracker:
    def __init__(self, value=0.0):
        raise NotImplementedError

    def get_value(self):
        raise NotImplementedError
