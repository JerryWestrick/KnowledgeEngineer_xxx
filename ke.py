from textual import on
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.events import Key
from textual.widgets import Header, Footer, RichLog

from memory_tree import MemoryTree,  DirTree
from file_editor import FileEditor
from file_system_event_handler import FSEHandler
from logger import Logger
# from messages import Info
from process_commands import ProcessCommands, ProcessCommand
from process_editor import ProcessEditor
from step_editor import StepEditor


class KEApp(App):
    wlog = Logger(namespace="KEApp", debug=False)
    BINDINGS = [
        ('d', 'toggle_dark', "Toggle dark mode"),
        ('q', 'quit', "Quit Application"),
    ]

    CSS_PATH = "ke.tcss"

    COMMANDS = App.COMMANDS | {ProcessCommands}
    clipboard: dict[str, str] = {}

    # pe_language = get_language("PromptEngineer")

    def compose(self) -> ComposeResult:
        """What Widgets is this app composed of?"""
        # self.log.info("In compose()")
        yield Header(show_clock=True)
        yield Footer()

        self.process_editor = ProcessEditor(id="process_editor")
        self.step_editor = StepEditor(id="step_editor")
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

    @on(FSEHandler.FileSystemChangeMessage)
    def fs_change(self, fs: FSEHandler.FileSystemChangeMessage):
        match fs.event_type:
            case 'created':
                pass

            case 'deleted':
                pass

            case 'moved':
                pass

            case 'modified':
                if fs.is_directory:
                    dirtree: DirTree = self.query_one("#directory_tree")
                    dirtree.reload_path(fs.src_path)

        self.wlog.info(f"{'fs_change':>15}:event_type={fs.event_type}, "
                       f"is_directory={fs.is_directory}, "
                       f"src_path={fs.src_path}, "
                       f"dst_path={fs.dst_path}"
                       )

    # @on(Info)
    # def log_info(self, msg: Info):
    #     self.wlog.info(f"{msg.func:>15}:{msg.msg}")
    #     return

    async def on_mount(self) -> None:
        self.event_handler = FSEHandler(self)  # Pass the watchdog_screen instance

    @on(Key)
    def check_key_event(self, event: Key):
        match event.key:
            case 'ctrl+up':
                rows = [s.value for s in self.grid.styles.grid_rows]
                rows[2] += 1
                rows_str = f"{rows[0]} {rows[1]}fr {rows[2]}fr"
                # self.wlog.info(f"grid_rows({rows_str})")
                self.grid.styles.grid_rows = rows_str

            case 'ctrl+down':
                rows = [s.value for s in self.grid.styles.grid_rows]
                if rows[2] == 1:
                    return

                rows[2] -= 1
                rows_str = f"{rows[0]} {rows[1]}fr {rows[2]}fr"
                self.grid.styles.grid_rows = rows_str

            case _:
                self.wlog.info(f"{event}")

    @on(ProcessCommand)
    def on_process_command(self, cmd: ProcessCommand) -> None:
        self.wlog.info(f"on_process_command({cmd})")
        match cmd.object_type:
            case "Process":

                pass
            case "Step":
                pass
            case "File":
                pass
            case "Debug":
                namespace, value = cmd.object_name.split('/')
                Logger.set_namespace(namespace, value)
                self.wlog.info(f"Set Debug {namespace} to {value}")
            case _:
                self.wlog.warn(f"Unknown object_type='{cmd.object_type}'")

    @on(StepEditor.StepAction)
    async def on_step_action(self, s: StepEditor.StepAction):
        if s.sname != '':
            self.wlog.info(f"Got StepAction('{s}')")
            await self.step_editor.step_action(s)

    @on(FileEditor.FileAction)
    async def on_file_action(self, f: FileEditor.FileAction):
        self.wlog.info(f"Got FileAction('{f}')")
        await self.file_editor.file_action(f)

    @on(DirTree.DirectoryAction)
    async def on_directory_action(self, f: DirTree.DirectoryAction):
        self.wlog.info(f"Got DirectoryAction('{f}')")
        await self.mt.directory_action(f)

    # @on(ProcessEditor.ProcessAction)
    # async def on_process_action(self, p: ProcessEditor.ProcessAction):
    #     self.wlog.info(f"on_process_action({p})")
    #     await self.process_editor.process_action(p)


if __name__ == "__main__":
    ke_app = KEApp()
    ke_app.run()
