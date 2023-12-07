import os
from functools import partial
from typing import Any

from rich.style import Style
from textual import on
from textual.app import App, ComposeResult, CSSPathType
from textual.binding import BindingType, Binding
from textual.command import Provider, Hits, Hit
from textual.containers import Grid, Horizontal
from textual.events import MouseDown, Click, MouseMove, Enter, Leave, MouseCapture, MouseUp, Key
from textual.message import Message
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Header, Footer, RichLog, Tree, Static, Label, Input, Button, DirectoryTree, MarkdownViewer, \
    Select, TextArea

from OpenAI_API_Costs import OpenAI_API_Costs
from db import DB
from logger import Logger
from step import Step
from processes import ProcessList, ProcessList_save

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


from tree_sitter_languages import get_language


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


class InputCP(Input):

    @on(MouseDown)
    def check_event(self, event: MouseDown):
        if event.ctrl:
            if event.button == 1:
                self.set_clipboard()
                event.stop()
            elif event.button == 3:
                self.get_clipboard()
                event.stop()

    @on(Key)
    def check_key_event(self, event: Key):
        if event.key == 'ctrl+o':
            self.set_clipboard()
            event.stop()
        elif event.key == 'ctrl+p':
            self.get_clipboard()
            event.stop()

    def set_clipboard(self):
        self.app.clipboard = {"text": self.value}

    def get_clipboard(self):
        if 'text' in self.app.clipboard:
            self.value = self.app.clipboard['text']


class StepEditor(Static):
    wlog: Logger = Logger(namespace="StepEditor", debug=True)
    pname: str = ''
    step: Step | None = None
    changes_are_internal: bool = False

    def compose(self) -> ComposeResult:
        self.border_title = 'Step Editor'

        self.fields = [
            # Step Name
            Label('Name:', id="name_lbl", classes="field_lbl"),
            InputCP("1", name="name", id="name_field", classes="field_input"),

            # Prompt Name
            # Label('Prompt Name:', id="prompt_name_lbl", classes="field_lbl"),
            Label('Prompt Name>', id="step_prompt_name_btn", classes="field_lbl"),
            InputCP("2", name="prompt_name", id="prompt_name_field", classes="field_input"),

            # Storage Path
            # Label('Storage Path:', id="storage_path_lbl", classes="field_lbl"),
            Label('Storage Path>', id="step_storage_path_btn", classes="field_lbl"),
            InputCP("3", name="storage_path", id="storage_path_field", classes="field_input"),

            # Text File
            # Label('Text File:', id="text_file_lbl", classes="field_lbl"),
            Label('Text File>', id="step_text_file_btn", classes="field_lbl"),
            InputCP("4", name="text_file", id="text_file_field", classes="field_input"),

            # Model
            Label('Model:', id="model_lbl", classes="field_lbl"),
            # Input("5", id="model_field", classes="field_input"),
            Select([(k, k) for k in OpenAI_API_Costs.keys()],
                   id="model_select", name="model",
                   classes="field_input",
                   allow_blank=True,
                   value='gpt-3.5-turbo'
                   ),

            # Temperature
            Label('Temperature:', id="temperature_lbl", classes="field_lbl"),
            InputCP("6", name="temperature", id="temperature_field", classes="field_input"),

            # Max Tokens
            Label('Max Tokens:', id="max_tokens_lbl", classes="field_lbl"),
            InputCP("7", name="max_tokens", id="max_tokens_field", classes="field_input"),
        ]

        yield Grid(*self.fields, id="step_fields_grid")

        self.step_exec_btn = Button("Execute", id="step_exec_btn", classes="small_btn hidden")
        self.step_save_btn = Button("Save", id="step_save_btn", classes="small_btn hidden")

        yield Horizontal(
            self.step_exec_btn, self.step_save_btn,
            id="step_btn_bar", classes="btn_bar"
        )

    async def step_action(self, sa: StepAction) -> None:

        self.pname: str = sa.pname
        self.border_title = f"Step Editor: {self.pname}/{sa.sname}"
        for s in ProcessList[sa.pname]:
            if s.name == sa.sname:
                self.step = s
                break

        for aWidget in self.fields:
            match aWidget.__class__.__name__:
                case 'Label':
                    continue

                case 'Button':
                    continue

                case 'Input' | 'InputCP':
                    name = aWidget.id[:-6]
                    value = getattr(self.step, name, None)
                    if value is None:
                        value = getattr(self.step.ai, name, None)
                    with self.prevent(Input.Changed):
                        aWidget.value = str(value)
                    continue

                case "Select":
                    name = aWidget.id[:-7]
                    value = getattr(self.step, name, None)
                    if value is None:
                        value = getattr(self.step.ai, name, None)
                    with self.prevent(Select.Changed):
                        aWidget.value = str(value)
                    continue

                case _:
                    self.wlog.error(f"Widget:{aWidget.id} is of unknown class {aWidget.__class__}")

        self.step_exec_btn.remove_class("hidden").label = f"Execute: {self.step.name}"

        if sa.cname == 'Select':
            return

        self.wlog.info(f"Running Worker to execute step: {self.pname}/{self.step.name}")
        self.run_worker(self.step.run(self.pname), exclusive=True)

    @on(Input.Changed)
    @on(Select.Changed)
    async def step_modified(self, c):
        if self.step is None:
            return

        self.step_save_btn.remove_class("hidden")
        self.step_exec_btn.add_class("hidden")

        if c.control.name in ["name", "prompt_name", "storage_path", "text_file"]:
            setattr(self.step, c.control.name, c.value)
            self.wlog.info(f"change step.{c.control.name} = {c.value}")

        if c.control.name in ["model", "temperature", "max_tokens"]:
            setattr(self.step.ai, c.control.name, c.value)
            self.wlog.info(f"change step.ai.{c.control.name} = {c.value}")
        return

    @on(Button.Pressed, "#step_save_btn")
    def save_process_list(self):
        self.step_save_btn.add_class("hidden")
        self.step_exec_btn.remove_class("hidden")
        ProcessList_save(ProcessList)

    @on(Button.Pressed, "#step_exec_btn")
    def exec_step(self):
        self.post_message(StepAction("Execute", self.pname, self.step.name))


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


class ProcessEditor(Static):
    wlog = Logger(namespace="ProcessSelector", debug=False)

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


class DirectoryChange(Message):
    """Notification of a change within a Directory"""

    def __init__(self, path: str, event_type: str):
        super().__init__()
        self.path: str = path
        self.path: str = event_type

class ThreadedEventHandler(FileSystemEventHandler):
    """
        This class is called from with in the watchdog THREAD...
        It can only call the functions:
        - post_message() and
        - call_from_thread()
    """
    def __init__(self, widget: Widget):
        self.widget: Widget = widget

    def on_created(self, event):
        self.widget.post_message(DirectoryChange(event.src_path, "created"))

    def on_deleted(self, event):
        self.widget.post_message(DirectoryChange(event.src_path, "deleted"))

    def handle_event(self, event, event_type):
        # Handle the event (file created or deleted)
        print(f"File {event.src_path} was {event_type}")



class DirTree(DirectoryTree):
    wlog: Logger = Logger(namespace="DirTree", debug=True)
    selected_file: str | None = None
    selected_directory: str | None = None

    # These are values used in a separate thread and not
    # to be used within normal Textual code



    BINDINGS: list[BindingType] = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("space", "toggle_node", "Toggle", show=False),
        Binding("up", "cursor_up", "Cursor Up", show=False),
        Binding("down", "cursor_down", "Cursor Down", show=False),
        Binding("shift+delete", "shift+delete", "Cut", show=True),
        Binding("insert", "insert", "Paste", show=True),
        Binding("ctrl+delete", "ctrl+delete", "Copy", show=True),
    ]

    @on(DirectoryTree.FileSelected)
    def file_selected(self, fs: DirectoryTree.FileSelected):
        path = str(fs.path)
        path = path.replace('Memory/', '')
        self.selected_file = path
        self.selected_directory = None

    @on(DirectoryTree.DirectorySelected)
    def directory_selected(self, fs: DirectoryTree.DirectorySelected):
        path = str(fs.path)
        path = path.replace('Memory/', '')
        self.selected_directory = path
        self.selected_file = None

    @on(MouseDown)
    def check_event(self, event: MouseDown):
        self.wlog.info(f"MouseDown({event}")
        if event.ctrl:
            if event.button == 1:
                self.set_clipboard()
                event.stop()

    @on(Key)
    def check_key_event(self, event: Key):
        self.wlog.info(f"Key({event}")
        match event.key:
            case 'ctrl+o':
                self.set_clipboard()
                event.stop()

            case 'delete':
                pass

            case 'insert':
                pass


    def set_clipboard(self):
        c = {}
        if self.selected_file:
            c['text'] = self.selected_file
        else:
            c['text'] = self.selected_directory

        self.app.clipboard = c


class MemoryTree(Static):
    wlog: Logger = Logger(namespace="MemoryTree", debug=False)

    def compose(self) -> ComposeResult:
        self.border_title = "Knowledge Storage"
        self.dirtree = DirTree("./Memory/", name="DirectoryTree", id="directory_tree")
        yield self.dirtree

    @on(DirectoryTree.FileSelected)
    def file_selected(self, fs: DirectoryTree.FileSelected):
        fs.prevent_default()
        self.post_message(FileAction("View", self.dirtree.selected_file))


class FileEditor(Static):
    db: DB = DB("Memory")
    wlog: Logger = Logger(namespace="FileEditor", debug=False)

    # pel = get_language("promptengineer")

    def compose(self) -> ComposeResult:
        self.border_title = "File Editor"

        self.md_viewer = MarkdownViewer("", show_table_of_contents=True, id="mdv", classes="hidden")
        yield self.md_viewer

        self.txt_editor = TextArea("", id="text_edit", classes="hidden")
        yield self.txt_editor

        self.edit_btn = Button("Edit", id="edit_btn", classes="hidden small_btn")
        self.view_btn = Button("View", id="view_btn", classes="hidden small_btn")

        self.save_btn = Button("Save", id="save_btn", classes="hidden small_btn")
        self.toc_btn = Button("<<<", id="toc_btn", classes="hidden small_btn")

        yield Horizontal(
            self.toc_btn,
            self.edit_btn,
            self.view_btn,
            self.save_btn,
            id="fe_btn_bar", classes="btn_bar",
        )

        self.pathname = ''
        self.known_extensions = {'.py': 'python', '.md': 'markdown'}

    def view_mode(self) -> None:
        self.txt_editor.add_class("hidden")
        self.md_viewer.remove_class("hidden")
        self.edit_btn.remove_class("hidden")
        self.toc_btn.remove_class("hidden")
        self.border_title = f"Viewing {self.pathname}"

    def edit_mode(self) -> None:
        self.txt_editor.remove_class("hidden")
        self.md_viewer.add_class("hidden")
        self.toc_btn.add_class("hidden")
        self.border_title = f"Editing {self.pathname}"

    async def file_action(self, f: FileAction) -> None:
        ext = os.path.splitext(f.name)[1]

        self.pathname = f.name

        if ext == '.md' and f.cmd == 'View':
            self.view_mode()
            self.view_btn.add_class("hidden")
            self.edit_btn.remove_class("hidden")
            # file_contents = self.db.get(f.name)
            full_path = f"{os.getcwd()}/Memory/{self.pathname}"
            await self.md_viewer.go(full_path)
            return

        if ext == '.md':
            self.edit_btn.add_class("hidden")
            self.view_btn.remove_class("hidden")
        else:
            self.edit_btn.add_class("hidden")
            self.view_btn.add_class("hidden")

        self.edit_mode()
        self.border_title = f"Editing {f.name}"
        # self.wlog.info(f"Known Languages: {self.txt_editor.available_languages}")
        ext = os.path.splitext(self.pathname)[1]
        if ext in self.known_extensions:
            self.txt_editor.language = self.known_extensions[ext]
        else:
            self.txt_editor.language = None
        try:
            self.txt_editor.load_text(self.db.read(self.pathname))
        except KeyError as ke:
            self.wlog.error(f"File not found {self.pathname}")
        return

    @on(Button.Pressed, selector="#toc_btn")
    def toggle_table_of_contents(self):
        self.md_viewer.show_table_of_contents = not self.md_viewer.show_table_of_contents
        if self.md_viewer.show_table_of_contents:
            self.toc_btn.label = '<<<'
        else:
            self.toc_btn.label = '>>>'

    @on(Button.Pressed, selector="#edit_btn")
    def switch_to_edit_mode(self):
        self.post_message(FileAction("Edit", self.pathname))

    @on(Button.Pressed, selector="#view_btn")
    def switch_to_view_mode(self):
        self.post_message(FileAction("View", self.pathname))

    @on(Button.Pressed, selector="#save_btn")
    def save_file(self):
        # self.wlog.info(f"Save {self.pathname} with >>{self.txt_editor.text}<<")
        self.db[self.pathname] = self.txt_editor.text
        self.save_btn.add_class("hidden")

    @on(TextArea.Changed, selector="#text_edit")
    def modified(self):
        self.save_btn.remove_class("hidden")
        self.wlog.info(f"TextArea(text_edit) value changed...")


class KEApp(App):
    wlog = Logger(namespace="KEApp", debug=False)
    BINDINGS = [
        ('d', 'toggle_dark', "Toggle dark mode"),
        ('q', 'quit', "Quit Application"),
    ]
    CSS_PATH = "ke.tcss"
    COMMANDS = App.COMMANDS | {ProcessCommands}
    clipboard: dict[str, str] = {}

    from tree_sitter_languages import get_language
    # pe_language = get_language("PromptEngineer")

    def compose(self) -> ComposeResult:
        """What Widgets is this app composed of?"""
        # self.log.info("In compose()")
        yield Header(show_clock=True)
        yield Footer()

        self.process_editor = ProcessEditor(id="process_editor")
        self.step_editor = StepEditor()
        self.mt = MemoryTree(id="memory_tree")
        self.file_editor = FileEditor(id="file_editor", classes="file_editor")
        self.rt_log = RichLog(id="logger", highlight=False, markup=True)
        self.rt_log.border_title = "Message Log"
        Logger.logger_widget = self.rt_log

        self.grid = Grid(
            self.process_editor,
            self.step_editor,
            self.mt,
            self.file_editor,
            self.rt_log,
            id="main_grid", classes="main_grid"
        )
        yield self.grid

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
