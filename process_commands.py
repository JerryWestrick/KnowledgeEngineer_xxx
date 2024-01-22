import os
from functools import partial
from typing import Any

from rich.style import Style
from textual.command import Provider, Hits, Hit
from textual.message import Message
from textual.screen import Screen

from db import DB
from logger import Logger
from processes import Processes


class ProcessCommand(Message):
    """Process Command"""

    def __init__(self, command: str, object_type: str, object_name: str) -> None:
        self.command: str = str(command)
        self.object_type: str = str(object_type)
        self.object_name: str = str(object_name)
        super().__init__()

    def __str__(self) -> str:
        return f"ProcessCommand(command={self.command}, object_type={self.object_type}, object_name={self.object_name})"


class ProcessCommands(Provider):
    """A command provider to Select/Execute A Process or a Step
       Or to edit a file...
    """
    db: DB = DB('Memory')
    proc: Processes("Processes")

    wlog: Logger = Logger(namespace="ProcessCommands", debug=False)

    def __init__(self, screen: Screen[Any], match_style: Style | None = None):
        super().__init__(screen, match_style)
        self.step_list = []

    async def startup(self) -> None:
        """Called once when the command palette is opened, prior to searching"""

        self.step_list = ["New Process First"]

        # All Debug On/Off
        for log in Logger.get_instances():
            debug_value = "Off" if log.debug else "On"
            self.step_list.append(f"Set Debug {log.namespace}/{debug_value}")

        # All Processes
        for p in self.proc.glob_files('*'):
            self.step_list.extend([f"Select Process {p}",
                                   f"Execute Process {p}",
                                   f"Delete Process {p}",
                                   f"New Step {p}/First"
                                   ])
            for s in self.proc.glob_files(f"{p}/*"):
                step_name = s.replace(".json", "")
                self.step_list.extend([f"Select Step {step_name}",
                                       f"Execute Step {step_name}",
                                       f"Delete Step {step_name}",
                                       f"New Step {step_name}"
                                       ])

        all_files = []
        for root, dirs, files in os.walk("./Memory"):
            for file in files:
                all_files.append(str(os.path.join(root, file)))

        for fn in all_files:
            sfn = fn[9:]
            self.step_list.extend([f"Edit File {sfn}", f"View File {sfn}", f"Delete File {sfn}"])

        # cr = "\n"
        # self.wlog.info(f"StepList: ({len(self.step_list)})")
        # for step in self.step_list:
        #     self.wlog.info(f"  {step}")

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)

        app = self.app
        # assert isinstance(app, ViewerApp)

        for path in self.step_list:
            score = matcher.match(path)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(path),
                    partial(self.parse_command, path),
                )

    def parse_command(self, cmd: str) -> [str]:
        self.wlog.info(f"Parsing command: {cmd}")
        (command, object_type, object_name) = cmd.split(' ', maxsplit=2)
        self.app.post_message(ProcessCommand(command, object_type, object_name))
