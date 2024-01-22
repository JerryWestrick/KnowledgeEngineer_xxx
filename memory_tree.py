import fnmatch
import os
import shutil
from enum import Enum
from functools import partial
from pathlib import Path
from typing import Any

from textual import on, work
from textual.app import ComposeResult
from textual.binding import BindingType, Binding
from textual.containers import Horizontal
from textual.events import MouseDown, Key
from textual.message import Message
from textual.widgets import DirectoryTree, Static, Button
from textual.widgets._tree import TreeNode, Tree
from textual.worker import Worker
from watchdog.events import FileSystemEventHandler

from db import DB
from dialogs.inputdialog import InputDialog
from dialogs.popup_menu import PopUpMenu
from dialogs.yes_no_dialog import YesNoDialog
from file_editor import FileEditor, FileActionCmd
from file_system_event_handler import FSEHandler
from logger import Logger

from watchdog.observers import Observer


class DirectoryActionCmd(Enum):
    CREATE = "CREATE"
    DELETE = "DELETE"
    MOVE = "MOVE"
    RENAME = "RENAME"


class DirTree(DirectoryTree):
    wlog: Logger = Logger(namespace="DirTree", debug=False)
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
        self.update_buttons()

    def compose(self) -> ComposeResult:
        self.dir_new_file_btn = Button("New File", id="dir_new_file_btn", classes="small_btn ")
        self.dir_del_dir_btn = Button(f"Del {self.selected_directory}", id="dir_del_dir_btn", classes="small_btn ")
        self.dir_new_dir_btn = Button("New Sub Dir", id="dir_new_dir_btn", classes="small_btn ")
        self.dir_del_back_btn = Button("Del  .~01~. files", id="dir_del_back_btn", classes="small_btn ")

        yield Horizontal(
            self.dir_new_file_btn, self.dir_del_dir_btn, self.dir_new_dir_btn, self.dir_del_back_btn,
            id="dir_btn_bar", classes="btn_bar"
        )

        self.file_view_file_btn = Button("view File", id="file_view_file_btn", classes="small_btn ")
        self.file_edit_file_btn = Button(f"Del {self.selected_directory}", id="file_edit_dir_btn", classes="small_btn ")
        self.file_del_file_btn = Button("New Sub Dir", id="file_del_dir_btn", classes="small_btn ")
        self.file_new_file_btn = Button("Del  .~01~. files", id="file_new_back_btn", classes="small_btn ")
        self.file_set_prompt_btn = Button("Set Prompt", id="file_set_prompt_btn", classes="small_btn ")
        yield Horizontal(
            self.file_view_file_btn, self.file_edit_file_btn, self.file_del_file_btn, self.file_new_file_btn,
            self.file_set_prompt_btn,
            id="file_btn_bar", classes="btn_bar"
        )

    def update_buttons(self):
        if self.selected_directory:
            self.query_one("#dir_btn_bar").remove_class("hidden")
            self.dir_new_file_btn.label = f"New File"
            self.dir_del_dir_btn.label = f"Del"
            self.dir_new_dir_btn.label = f"New Sub Dir"
            self.dir_del_back_btn.label = f"Del  .~01~. files"
        else:
            self.query_one("#dir_btn_bar").add_class("hidden")

        if self.selected_file:
            self.query_one("#file_btn_bar").remove_class("hidden")
            self.file_view_file_btn.label = f"View "
            self.file_edit_file_btn.label = f"Edit "
            self.file_del_file_btn.label = f"Del "
            self.file_new_file_btn.label = f"New File"
            self.file_set_prompt_btn.label = f"Set Prompt"
        else:
            self.query_one("#file_btn_bar").add_class("hidden")

    def create_new_file(self, old_file_name: str, new_file_name: str) -> None:
        dir_path = os.path.dirname(f"{old_file_name}")  # Extract directory of old file
        new_file_path = os.path.join(dir_path, new_file_name)
        self.wlog.info(
            f"create_new_file(old_file_name={old_file_name},new_file_name={new_file_name}):{self.db.path}/{new_file_path}")
        open(f"{self.db.path}/{new_file_path}", 'w').close()  # Create the new file
        # self.post_message(FileEditor.FileAction(FileActionCmd.VIEW, new_file_path))

    def create_new_dir(self, dir_path: str, dir_name: str) -> None:
        new_dir_path = f"{self.db.path}/{dir_path}/{dir_name}"
        self.wlog.info(f"Create a new directory {new_dir_path}")
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
        self.update_buttons()

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

    @on(Button.Pressed)
    async def on_button_pressed(self, event):
        self.wlog.info(f"Got ButtonPressed({event.button})")
        match event.button.id:
            case "file_view_file_btn":
                self.post_message(FileEditor.FileAction(FileActionCmd.VIEW, path))
            case "file_edit_file_btn":
                self.post_message(FileEditor.FileAction(FileActionCmd.EDIT, path))
            case "file_del_file_btn":
                self.post_message(self.DirectoryAction(DirectoryActionCmd.DELETE, path))
            case "file_new_file_btn":
                new_name = await self.app.push_screen_wait(
                    InputDialog("New File Dialog", "Name of New file:",
                                offset=(event.screen_x, event.screen_y)
                                )
                )
                self.create_new_file(None, new_name)
            case "file_set_prompt_btn":
                self.wlog.info(f"Set Prompt clicked!!!!!")

            case "dir_new_file_btn":
                self.wlog.info(f"clicked button {event.button.id}")
            case "dir_del_dir_btn":
                self.wlog.info(f"clicked button {event.button.id}")
            case "dir_new_dir_btn":
                self.wlog.info(f"clicked button {event.button.id}")
            case "dir_del_back_btn":
                self.wlog.info(f"clicked button {event.button.id}")



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
            self.create_new_file(
                f"{self.selected_directory}/t.tmp",
                f"{new_file_name}"
            )
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
        self.watchDirectory = "./Memory/"
        self.dirtree = DirTree(self.watchDirectory, name="DirectoryTree", id="directory_tree")
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

    async def on_mount(self) -> None:
        self.dirtree.root.expand_all()  # Load all the items so that we can access Them when needed
        self.observer = Observer()
        self.event_handler = FSEHandler(self, self.watchDirectory)  # Pass the watchdog_screen instance
        # self.observer.schedule(self.event_handler, self.watchDirectory, recursive=True)
        # t = Worker(self, self.observer.start(), name="WatchDog", description="Separate Thread running WatchDog",
        #            thread=True)
        # self.workers.add_worker(t, start=False, exclusive=True)

    def find_child_node(self, parent: TreeNode, child_names: [str]) -> TreeNode[Any] | None:
        self.wlog.info(f"Looking for {child_names}")

        # if it is a child of the root node...
        if not child_names:
            return parent

        for child in parent.children:
            self.wlog.info(f"Looking at {child.label}")
            if str(child.label) == child_names[0]:
                child_names.pop(0)
                if not child_names:
                    return child
                else:
                    return self.find_child_node(child, child_names)
        return None

    @on(FSEHandler.FileSystemChangeMessage)
    async def fs_change(self, fs: FSEHandler.FileSystemChangeMessage):
        self.wlog.info(f"{'fs_change':>15}:[cyan]event_type=[/]{fs.event_type}, "
                       f"[cyan]is_directory=[/]{fs.is_directory}, "
                       f"[cyan]src_path=[/]{fs.src_path}, "
                       f"[cyan]dst_path=[/]{fs.dst_path}"
                       )

        match fs.event_type:
            case 'modified':
                pass

            case 'moved':
                src_names = fs.src_path.split('/')[2:]
                src_name = src_names.pop(-1)

                dst_names = fs.dst_path.split('/')[2:]
                dst_name = dst_names.pop(-1)

                if src_names == dst_names:
                    self.wlog.info(f"rename of file {src_name} to {dst_name} in directory {src_names}")
                    child_node = self.find_child_node(self.dirtree.root, fs.src_path.split('/')[2:])
                    if child_node:
                        child_node.label = dst_name
                    # child_node = self.find_child_node(self.dirtree.root, fs.src_path.split('/')[2:])
                else:
                    self.wlog.info(f"move file from {fs.src_path} to {fs.dst_path}")
                    await self.fs_change(FSEHandler.FileSystemChangeMessage('deleted',
                                                                            fs.is_directory,
                                                                            fs.src_path,
                                                                            ''))
                    await self.fs_change(FSEHandler.FileSystemChangeMessage('created',
                                                                            fs.is_directory,
                                                                            fs.dst_path,
                                                                            ''))

            case 'created':
                names = fs.src_path.split('/')[2:]
                file_name = names.pop(-1)
                child_node = self.find_child_node(self.dirtree.root, names)
                if child_node:
                    if fs.is_directory:
                        self.wlog.info(f"Adding dir {file_name} to dir {child_node.label}")
                        child_node.add(file_name)
                    else:
                        self.wlog.info(f"Adding file {file_name} to dir {child_node.label}")
                        child_node.add_leaf(file_name)
                else:
                    self.wlog.info(f"node not Found {fs.src_path}")

            case 'deleted':
                child_node = self.find_child_node(self.dirtree.root, fs.src_path.split('/')[2:])
                if child_node:
                    self.wlog.info(f"deleting node {child_node.label}")
                    child_node.remove()
                else:
                    self.wlog.info(f"node not Found {fs.src_path}")

    @on(FSEHandler.Info)
    def log_info(self, msg: FSEHandler.Info):
        self.wlog.info(f"{msg.func:>15}:{msg.msg}")
        return
