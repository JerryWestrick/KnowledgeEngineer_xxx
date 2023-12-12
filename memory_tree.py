import os
from functools import partial

from textual import on
from textual.app import ComposeResult
from textual.binding import BindingType, Binding
from textual.events import MouseDown, Key
from textual.widgets import DirectoryTree, Static
from textual.widgets._tree import TreeNode

from dialogs.input_dialog import Input_Dialog
from dialogs.popup_menu import PopUpMenu
from dialogs.yes_no_dialog import YesNoDialog
from logger import Logger
from messages import FileAction, FileActionCmd


class DirTree(DirectoryTree):
    wlog: Logger = Logger(namespace="DirTree", debug=True)
    selected_file: str | None = None
    selected_directory: str | None = None


    # Have not got these bindings to work yet...
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
        self.wlog.info(f"")

    def create_new_file(self, old_file_name: str, new_file_name: str) -> None:
        dir_path = os.path.dirname(f"{old_file_name}")  # Extract directory of old file
        new_file_path = os.path.join(dir_path, new_file_name)
        self.wlog.info(f"Create new file {new_file_name} as sibling of path/file: {old_file_name}")
        self.wlog.info(f"Create new file {new_file_path}")
        open("Memory/" + new_file_path, 'a').close()  # Create the new file
        self.post_message(FileAction('View', new_file_path))

    @on(DirectoryTree.DirectorySelected)
    def directory_selected(self, fs: DirectoryTree.DirectorySelected):
        path = str(fs.path)
        path = path.replace('Memory/', '')
        self.selected_directory = path
        self.selected_file = None

    def do_file_menu_option(self, event: MouseDown, path: str, option: str):
        self.wlog.info(f"File Menu: {option} {path}")
        keywords = str(option).split(' ')
        if keywords[1] != 'File':
            self.wlog.warn(f"Expected Second keyword in '{option}' to be 'File' not '{keywords[1]}'.")
            return

        match keywords[0]:
            case 'View' | 'Edit' | 'Delete':
                self.post_message(FileAction(keywords[0], path))

            case 'New':
                self.app.push_screen(
                    Input_Dialog("New File Dialog", "Name of New file:",
                                 offset=(event.screen_x, event.screen_y)
                                 ),
                    partial(self.create_new_file, self.selected_file)
                )

    def do_directory_menu_option(self, path: str, option: str):
        self.wlog.info(f"Dir Menu: {option} {path}")

    @on(MouseDown)
    def check_event(self, event: MouseDown):
        self.wlog.info(f"MouseDown({event}")

        match event.button:

            case 1:
                if event.ctrl:
                    self.set_clipboard()
                    event.stop()
            case 3:
                if self.selected_file:
                    self.app.push_screen(
                        PopUpMenu(
                            f"Popup File: {self.selected_file}",
                            ['Delete File', 'View File', 'Edit File', 'New File', ],
                            offset=(event.screen_x, event.screen_y)

                        ),
                        partial(self.do_file_menu_option, event, self.selected_file),
                    )
                elif self.selected_directory:
                    self.app.push_screen(
                        PopUpMenu(
                            f"Popup Directory: {self.selected_directory}",
                            ['Delete Directory', 'New Directory After', ],
                            offset=(event.screen_x, event.screen_y)

                        ),
                        partial(self.do_directory_menu_option, self.selected_directory),
                    )

    @on(Key)
    def check_key_event(self, event: Key):
        match event.key:
            case 'ctrl+o':
                self.set_clipboard()
                event.stop()

            case 'delete':
                if self.selected_file:
                    self.app.push_screen(
                        YesNoDialog(
                            "File Delete",
                            f"Are you sure you want to delete the file {self.selected_file}?",
                        ),
                        partial(self.delete_file, self.selected_file),
                    )

                    event.prevent_default()
                    event.stop(True)
                    return

                if self.selected_directory:
                    self.app.push_screen(
                        YesNoDialog(
                            "Directory Deletion",
                            f"Are you sure you want to delete the directory {self.selected_directory}?",
                        ),
                        partial(self.delete_directory, self.selected_directory),
                    )

                    event.prevent_default()
                    event.stop(True)
                    return

                return

            case _:
                self.wlog.info(f"{event}")

    def find_node(self, path: str) -> TreeNode:
        anode: TreeNode = self.root

        for child_label in path.split('/')[1:]:
            for child in anode.children:
                if child.label == child_label:
                    anode = child
        return anode

    def delete_file(self) -> None:
        self.wlog.info(f"Delete file: Memory/{self.selected_file}")
        self.selected_file = None

    def delete_directory(self) -> None:
        self.wlog.info(f"Delete of directory: Memory/{self.selected_directory}")
        self.selected_directory = None
        # shutil.rmtree(f"Memory/{path}")

    def reload_path(self, path: str):
        anode: TreeNode = self.find_node(path)
        self.reload_node(anode)
        self.root.expand_all()

    def set_clipboard(self):
        c = {}
        if self.selected_file:
            c['text'] = self.selected_file
        else:
            c['text'] = self.selected_directory

        self.app.clipboard = c

    async def on_mount(self) -> None:
        self.root.expand_all()  # Load all the items so that we can access Them when needed


class MemoryTree(Static):
    wlog: Logger = Logger(namespace="MemoryTree", debug=False)

    def compose(self) -> ComposeResult:
        self.border_title = "Knowledge Storage"
        self.dirtree = DirTree("./Memory/", name="DirectoryTree", id="directory_tree")
        yield self.dirtree

    @on(DirectoryTree.FileSelected)
    def file_selected(self, fs: DirectoryTree.FileSelected):
        fs.prevent_default()
        self.post_message(FileAction(FileActionCmd.VIEW, self.dirtree.selected_file))


