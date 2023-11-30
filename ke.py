import os
from functools import partial
from typing import Any

from rich.style import Style
from textual.app import App, ComposeResult, CSSPathType
from textual.command import Provider, Hits, Hit
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Header, Footer, RichLog, Tree, Static, Label, Input, Button, DirectoryTree, MarkdownViewer

from db import DB
from logger import Logger
from step import Step
from processes import ProcessList


def make_label(key: str) -> str:
    words = key.split('_')
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)


class StepAction(Message):
    """Step selected message."""

    def __init__(self, cname: str, pname: str, sname: str) -> None:
        self.cname: str = str(cname)
        self.pname: str = str(pname)
        self.sname: str = str(sname)
        super().__init__()


class FileAction(Message):
    """Action on a file in memory"""

    def __init__(self, cmd: str, name: str) -> None:
        self.cmd: str = str(cmd)
        self.name: str = str(name)
        super().__init__()


class StepEditor(Static):
    wlog: Logger = Logger(namespace="StepEditor", debug=True)
    pname: str = ''
    step: Step | None = None
    step_widgets = ['name', 'prompt_name', 'storage_path', 'text_file']
    ai_widgets = ['model', 'temperature', 'max_tokens']

    async def step_action(self, sa: StepAction) -> None:

        self.pname: str = sa.pname
        self.border_title = f"Step {self.pname}/{sa.sname} Editor"
        for s in ProcessList[sa.pname]:
            if s.name == sa.sname:
                self.step = s

        for wid in self.step_widgets:
            self.query_one(f"#{wid}").value = str(getattr(self.step, wid))
        for wid in self.ai_widgets:
            self.query_one(f"#{wid}").value = str(getattr(self.step.ai, wid))

        self.query_one(Button).remove_class("hidden").label = f"[Execute: {self.step.name}]"

        if sa.cname == 'Select':
            return
        self.wlog.info(f"Running Worker to execute step: {self.pname}/{self.step.name}")
        self.run_worker(self.step.run(self.pname), exclusive=True)

    def compose(self) -> ComposeResult:
        self.border_title = 'Step Editor'
        for k in self.step_widgets:
            yield Label(f"{make_label(k):>13}: ", id=f"{k}_lbl", classes='field-name')
            yield Input("", id=k, classes='field-input')
        for k in self.ai_widgets:
            yield Label(f"{make_label(k):>13}: ", id=f"{k}_lbl", classes='field-name')
            yield Input("", id=k, classes='field-input')

        yield Static("", id="filler")

        b = Button("Execute ", id="exec-btn")
        yield b

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        await self.step_action(StepAction("Execute", self.pname, self.name))


class ProcessCommands(Provider):
    """A command provider to Select/Execute A Process or a Step
       Or to edit a file...
    """
    db: DB = DB('Memory')

    wlog: Logger = Logger(namespace="ProcessCommands")

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
                all_files.append(os.path.join(root, file))

        edit_list = [f"Edit {f[9:]}" for f in all_files]
        # self.wlog.info(f"fileList: {edit_list}")
        self.step_list.extend(edit_list)

        # self.wlog.info(f"StepList: {self.step_list}")

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
                elif command in ['Edit']:
                    yield Hit(
                        score,
                        matcher.highlight(path),
                        partial(app.on_file_action, FileAction(command, f"Memory/{rest}")),
                    )


class ProcessEditor(Static):
    wlog = Logger(namespace="ProcessSelector")

    def compose(self) -> ComposeResult:
        tree: Tree[dict] = Tree("Processes")
        tree.root.expand()
        tree.show_root = False
        for proc_name in ProcessList.keys():
            procedure = tree.root.add(proc_name)
            for step in ProcessList[proc_name]:
                procedure.add_leaf(step.name, data=step)
        self.border_title = 'Process List'
        yield tree

    def on_tree_node_selected(self, e):
        e.prevent_default()
        # self.wlog.info(f"Selected: {e.node.label} {len(e.node.children)} children")
        if e.node.data:
            # self.wlog.info(f"Selected: {e.node.data.prompt_name}")
            self.post_message(StepAction("Select", e.node.parent.label, e.node.label))


class MemoryTree(Static):

    wlog: Logger = Logger(namespace="MemoryTree")

    def compose(self) -> ComposeResult:
        self.border_title = "Knowledge Storage"
        self.dirtree = DirectoryTree("./Memory/")
        yield self.dirtree

    def on_directory_tree_file_selected(self, fs: DirectoryTree.FileSelected):
        fs.prevent_default()
        # self.wlog.info(f"Selected: {fs.node.label}")
        # self.wlog.info(f"Selected: {fs.path}")
        self.post_message(FileAction("Edit", str(fs.path)))


class FileEditor(Static):
    db: DB = DB("Memory")
    wlog: Logger = Logger(namespace="FileEditor")

    def compose(self) -> ComposeResult:
        self.border_title = "File Editor"
        self.md_viewer = MarkdownViewer("", show_table_of_contents=True, id="mdv")
        yield self.md_viewer

    async def file_action(self, f: FileAction) -> None:
        if f.cmd == 'Edit':
            # file_contents = self.db.get(f.name)
            full_path = f"{os.getcwd()}/{f.name}"
            await self.md_viewer.go(full_path)
            # self.wlog.info(f"Current directory is {os.getcwd()}")


class KEApp(App):
    wlog = Logger(namespace="KEApp", debug=False)
    BINDINGS = [
        ('d', 'toggle_dark', "Toggle dark mode"),
        ('q', 'quit', "Quit Application"),
        ('p', 'procs', "Dump Processes")
    ]
    CSS_PATH = "ke.tcss"
    COMMANDS = App.COMMANDS | {ProcessCommands}

    def compose(self) -> ComposeResult:
        """What Widgets is this app composed of?"""
        # self.log.info("In compose()")
        yield Header(show_clock=True)
        yield Footer()

        yield ProcessEditor(id="process-editor")
        self.step_editor = StepEditor()
        yield self.step_editor

        self.mt = MemoryTree(id="memory-tree")
        yield self.mt

        self.file_editor = FileEditor(id="file-editor")
        yield self.file_editor

        l = RichLog(id="logger", highlight=True, markup=True)
        l.border_title = "Message Log"
        Logger.logger_widget = l
        yield l
        self.wlog.info(f"Processes Loaded")

    async def on_step_action(self, s: StepAction):
        # self.wlog.info(f"Got SelectStep('{s.cname}', '{s.pname}','{s.sname}')")
        if s.sname != '':
            await self.step_editor.step_action(s)

    async def on_file_action(self, f: FileAction):
        self.wlog.info(f"Got FileAction('{f.cmd}', '{f.name}')")
        if f.name != '':
            await self.file_editor.file_action(f)


if __name__ == "__main__":
    keapp = KEApp()
    keapp.run()
# @Done Add file browser/editor windows...
# @Done fix costs estimation...
# @Todo Directory Watcher...
# @Todo Fix Snake6 process
# @Todo Make Documentation
# @Done command Execute locks screen, while Button Execute frees it
# @Todo allow parallel conversations to chatGPT.
# @Done change logging of chat msgs to show conversation (to allow for above)
# @Done The Step Editor needs working (drop down for Model etc)
# @Todo Fix execute Process
