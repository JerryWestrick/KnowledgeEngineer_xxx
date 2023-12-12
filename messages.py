from enum import Enum

from textual.message import Message


class StepAction(Message):
    """Step selected message."""

    def __init__(self, cname: str, pname: str, sname: str) -> None:
        self.cname: str = str(cname)
        self.pname: str = str(pname)
        self.sname: str = str(sname)
        super().__init__()


class FileActionCmd(Enum):
    CREATE = "CREATE"
    DELETE = "DELETE"
    MOVE = "MOVE"
    UPDATE = "UPDATE"
    VIEW = "VIEW"
    EDIT = "EDIT"
    RENAME = "RENAME"


class FileAction(Message):
    def __init__(self, cmd: FileActionCmd, name: str):
        super().__init__()
        self.cmd = cmd
        self.name = name


class FileSystemChangeMessage(Message):
    """ A Notification of a change to a directory"""

    def __init__(self, event_type: str, is_directory: bool, src_path: str, dst_path: str = None):
        super().__init__()
        self.event_type: str = event_type
        self.is_directory: bool = is_directory
        self.src_path: str = src_path
        self.dst_path: str = dst_path


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
