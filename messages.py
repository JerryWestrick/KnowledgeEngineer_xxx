from enum import Enum

from textual.message import Message



class Info(Message):
    """ A Notification of a change to a directory"""

    def __init__(self, func: str, msg: str):
        super().__init__()
        self.func: str = func
        self.msg: str = msg


class DirectoryChange(Message):
    """Notification of a change within a Directory"""

    def __init__(self, path: str, event_type: str):
        super().__init__()
        self.path: str = path
        self.path: str = event_type
