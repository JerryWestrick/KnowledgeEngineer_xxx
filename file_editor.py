import os
from enum import Enum

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Static, MarkdownViewer, TextArea, Button

from db import DB
from logger import Logger


class FileActionCmd(Enum):
    CREATE = "CREATE"
    DELETE = "DELETE"
    MOVE = "MOVE"
    UPDATE = "UPDATE"
    VIEW = "VIEW"
    EDIT = "EDIT"
    RENAME = "RENAME"


class FileEditor(Static):
    db: DB = DB("Memory")
    wlog: Logger = Logger(namespace="FileEditor", debug=False)

    class FileAction(Message):
        def __init__(self, cmd: FileActionCmd, name: str):
            super().__init__()
            self.cmd = cmd
            self.name = name

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
        self.post_message(self.FileAction("Edit", self.pathname))

    @on(Button.Pressed, selector="#view_btn")
    def switch_to_view_mode(self):
        self.post_message(self.FileAction("View", self.pathname))

    @on(Button.Pressed, selector="#save_btn")
    def save_file(self):
        # self.wlog.info(f"Save {self.pathname} with >>{self.txt_editor.text}<<")
        self.db[self.pathname] = self.txt_editor.text
        self.save_btn.add_class("hidden")

    @on(TextArea.Changed, selector="#text_edit")
    def modified(self):
        self.save_btn.remove_class("hidden")
        self.wlog.info(f"TextArea(text_edit) value changed...")


