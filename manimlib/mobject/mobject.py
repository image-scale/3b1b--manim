"""Base Mobject class."""


class Mobject:
    def __init__(self):
        raise NotImplementedError

    def move_to(self, target):
        raise NotImplementedError
