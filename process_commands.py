import os
from functools import partial
from typing import Any

from rich.style import Style
from textual.command import Provider, Hits, Hit
from textual.screen import Screen

from db import DB
from logger import Logger
from messages import StepAction, FileAction
from processes import ProcessList


class ProcessCommands(Provider):
    """A command provider to Select/Execute A Process or a Step
       Or to edit a file...
    """
    db: DB = DB('Memory')

    wlog: Logger = Logger(namespace="ProcessCommands", debug=False)

    def __init__(self, screen: Screen[Any], match_style: Style | None = None):
        super().__init__(screen, match_style)
        self.step_list = []

    async def startup(self) -> None:
        """Called once when the command palette is opened, prior to searching"""

        for p, v in ProcessList.items():
            self.step_list.extend([f"Select {p}", f"Execute {p}"])
            self.step_list.extend([f"Select {p}/{s.name}" for s in v])
            self.step_list.extend([f"Execute {p}/{s.name}" for s in v])

        all_files = []
        for root, dirs, files in os.walk("./Memory"):
            for file in files:
                all_files.append(str(os.path.join(root, file)))

        for fn in all_files:
            sfn = fn[9:]
            self.step_list.append(f"Edit {sfn}")
            self.step_list.append(f"View {sfn}")

        self.wlog.info(f"StepList: ({len(self.step_list)}) {self.step_list}")

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)

        app = self.app
        # assert isinstance(app, ViewerApp)

        for path in self.step_list:
            score = matcher.match(path)
            if score > 0:
                command, rest = path.split(' ', 1)
                if command in ['Select', 'Execute']:
                    if '/' in rest:
                        pname, sname = rest.split('/')
                    else:
                        pname = rest
                        sname = ''
                    yield Hit(
                        score,
                        matcher.highlight(path),
                        partial(app.on_step_action, StepAction(command, pname, sname)),
                    )
                elif command in ['Edit', 'View']:
                    yield Hit(
                        score,
                        matcher.highlight(path),
                        partial(app.on_file_action, FileAction(command, f"{rest}")),
                    )

