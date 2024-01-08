import fnmatch
import os
import shutil
from enum import Enum
from functools import partial

from textual import on, work
from textual.app import ComposeResult
from textual.binding import BindingType, Binding
from textual.events import MouseDown, Key
from textual.message import Message
from textual.widgets import DirectoryTree, Static
from textual.widgets._tree import TreeNode

from db import DB
from dialogs.inputdialog import InputDialog
from dialogs.popup_menu import PopUpMenu
from dialogs.yes_no_dialog import YesNoDialog
from file_editor import FileEditor, FileActionCmd
from logger import Logger


class DirectoryActionCmd(Enum):
    CREATE = "CREATE"
    DELETE = "DELETE"
    MOVE = "MOVE"
    RENAME = "RENAME"


class DirTree(DirectoryTree):
    wlog: Logger = Logger(namespace="DirTree", debug=True)
    selected_file: str | None = None
    selected_directory: str | None = None
    db: DB = DB("Memory")

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

    class DirectoryAction(Message):
        def __init__(self, cmd: DirectoryActionCmd, name: str):
            super().__init__()
            self.cmd = cmd
            self.name = name

        def __str__(self) -> str:
            return f"DirectoryAction(cmd={self.cmd}, name={self.name})"

    @on(DirectoryTree.FileSelected)
    def file_selected(self, fs: DirectoryTree.FileSelected):
        path = str(fs.path)
        path = path.replace('Memory/', '')
        self.selected_file = path
        self.selected_directory = None
        self.wlog.info(f"file_selected({path})")
        self.post_message(FileEditor.FileAction(FileActionCmd.VIEW, path))

    def create_new_file(self, old_file_name: str, new_file_name: str) -> None:
        dir_path = os.path.dirname(f"{old_file_name}")  # Extract directory of old file
        new_file_path = os.path.join(dir_path, new_file_name)
        self.wlog.info(
            f"create_new_file(old_file_name={old_file_name},new_file_name={new_file_name}):Memory/{new_file_path}")
        open("Memory/" + new_file_path, 'a').close()  # Create the new file
        # self.post_message(FileEditor.FileAction(FileActionCmd.VIEW, new_file_path))

    def create_new_dir(self, dir_path: str, dir_name: str) -> None:
        new_dir_path = f"Memory/{dir_path}/{dir_name}"
        try:
            os.mkdir(new_dir_path)  # Create the new directory
        except FileExistsError:
            self.wlog.warn(f"Directory '{new_dir_path}' already exists.")
        except Exception as e:
            self.wlog.error(f"An error occurred while creating the directory: {e}")

    @on(DirectoryTree.DirectorySelected)
    def directory_selected(self, fs: DirectoryTree.DirectorySelected):
        path = str(fs.path)
        path = path.replace('Memory/', '')
        self.selected_directory = path
        self.selected_file = None

    async def do_file_menu_option(self, event: MouseDown, path: str, option: str):
        self.wlog.info(f"File Menu: {option} {path}")
        keywords = str(option).split(' ')
        if keywords[1] != 'File':
            self.wlog.warn(f"Expected Second keyword in '{option}' to be 'File' not '{keywords[1]}'.")
            return

        match keywords[0]:
            case 'View':
                self.post_message(FileEditor.FileAction(FileActionCmd.VIEW, path))

            case 'Edit':
                self.post_message(FileEditor.FileAction(FileActionCmd.EDIT, path))

            case 'Delete':
                self.post_message(self.DirectoryAction(DirectoryActionCmd.DELETE, path))

            case 'New':
                new_name = await self.app.push_screen_wait(
                    InputDialog("New File Dialog", "Name of New file:",
                                offset=(event.screen_x, event.screen_y)
                                )
                )
                self.create_new_file(None, new_name)

    def find_files(self, directory, pattern):
        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    yield filename

    async def do_directory_menu_option(self, event: MouseDown, path: str, option: str):
        self.wlog.info(f"Dir Menu: '{option}' {path}")

        if 'New File' == str(option):
            self.wlog.info(f"directory_option({option})")
            new_file_name = await self.app.push_screen_wait(
                InputDialog("New File Dialog", "Name of New file:",
                            offset=(event.screen_x, event.screen_y)
                            )
            )
            self.create_new_file(f"{self.selected_directory}/t.tmp", new_file_name)
            return

        if 'Delete Directory' == str(option):
            confirmed: bool = await self.app.push_screen_wait(
                YesNoDialog("Delete Directory with all contents", f"Delete {path}:",
                            offset=(event.screen_x, event.screen_y)
                            )
            )
            self.delete_directory(self.selected_directory, confirmed)
            return

        if 'New Sub-Directory' == str(option):
            self.wlog.info(f"directory_option({option})")
            new_dir_name = await self.app.push_screen_wait(
                InputDialog("New Dir Dialog", "Name of New directory:",
                            offset=(event.screen_x, event.screen_y)
                            )
            )
            self.create_new_dir(self.selected_directory, new_dir_name)
            return

        if 'Clean Up .~01~. files' == str(option):
            self.wlog.info(f"directory_option({option})")

            self.db.delete_memory_backup(self.selected_directory)
            # for filename in self.find_files(f'Memory/{self.selected_directory}', '*.~*~.*'):
            #     self.wlog.info(f'About to delete {filename}')
            #     os.remove(filename)
            return

    @work
    async def do_popup_menu(self, event: MouseDown):
        if self.selected_file:
            file_cmd = await self.app.push_screen_wait(
                PopUpMenu(
                    f"Popup File: {self.selected_file}",
                    ['Delete File', 'View File', 'Edit File', 'New File', ],
                    offset=(event.screen_x, event.screen_y)
                )
            )
            await self.do_file_menu_option(event, self.selected_file, file_cmd)
        elif self.selected_directory:
            menu_cmd = await self.app.push_screen_wait(
                PopUpMenu(
                    f"Popup Directory: {self.selected_directory}",
                    ['Delete Directory', 'New Sub-Directory', 'New File', 'Clean Up .~01~. files'],
                    offset=(event.screen_x, event.screen_y)
                )
            )
            await self.do_directory_menu_option(event, f"{self.selected_directory}/t.txt", menu_cmd)

    @on(MouseDown)
    async def check_event(self, event: MouseDown):
        self.wlog.info(f"MouseDown({event}")

        match event.button:
            case 1:
                if event.ctrl:
                    self.set_clipboard()
                    event.stop()

            case 3:
                self.do_popup_menu(event)
                event.stop()

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

    def recurse(self, treenode: TreeNode):
        children = []
        for child in treenode.children:
            children.append(self.recurse(child))
        return treenode, treenode.is_expanded, children

    def expand_list(self, anode, is_expanded, children):

        self.wlog.info(f"Expanded List: {anode}")
        if is_expanded:
            anode.expand()

        for child, is_child_expanded, grand_children in children:
            self.expand_list(child, is_child_expanded, grand_children)

    def delete_file(self) -> None:
        self.wlog.info(f"Delete file: Memory/{self.selected_file}")
        os.remove(self.selected_file)
        self.selected_file = None

    def delete_directory(self, path: str, do_it: bool) -> None:
        if do_it:
            self.wlog.info(f"Delete of directory: Memory/{path}")
            shutil.rmtree(f"Memory/{path}")
            self.selected_directory = None

    def reload_path(self, path: str):
        # rnode, is_expanded, children = self.recurse(self.root)
        # anode: TreeNode = self.find_node(path)
        # self.reload_node(anode)  # wait till all is reloaded
        # self.root.expand_all()
        # self.wlog.info(f"Back from reload_node")
        # self.expand_list(rnode, is_expanded, children)
        pass

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
        # self.post_message(FileEditor.DirectoryAction(DirectoryActionCmd.VIEW, self.dirtree.selected_file))

    async def directory_action(self, f: DirTree.DirectoryAction) -> None:
        self.pathname = f.name
        ext = os.path.splitext(f.name)[1]
        self.wlog.info(f"file_action({f.cmd}, '{f.name}')")

        match f.cmd:
            case DirectoryActionCmd.MOVE:
                pass

            case DirectoryActionCmd.CREATE:
                pass

            case DirectoryActionCmd.DELETE:
                try:
                    os.remove(f"Memory/{f.name}")
                except FileNotFoundError:
                    self.wlog.error("File not found")
                except PermissionError:
                    self.wlog.error("Permission denied ")
                except Exception as e:
                    self.wlog.error(f"An error occurred while deleting file: {e}")

            case DirectoryActionCmd.RENAME:
                pass
