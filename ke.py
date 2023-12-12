from textual import on
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.events import Key
from textual.widgets import Header, Footer, RichLog
from textual.worker import Worker
from watchdog.observers import Observer

from memory_tree import MemoryTree
from file_editor import FileEditor
from file_system_event_handler import FSEHandler
from logger import Logger
from messages import FileAction, StepAction, FileSystemChangeMessage, Info
from process_commands import ProcessCommands
from process_editor import ProcessEditor
from step_editor import StepEditor


class KEApp(App):
    wlog = Logger(namespace="KEApp", debug=True)
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

    @on(FileSystemChangeMessage)
    def fs_change(self, fs: FileSystemChangeMessage):
        match fs.event_type:
            case 'created':
                pass

            case 'deleted':
                pass

            case 'moved':
                pass

            case 'modified':
                if fs.is_directory:
                    self.query_one("#directory_tree").reload_path(fs.src_path)

        self.wlog.info(f"{'fs_change':>15}:[cyan]event_type={fs.event_type}, "
                       f"is_directory={fs.is_directory}, "
                       f"src_path={fs.src_path}, "
                       f"dst_path={fs.dst_path}[/]"
                       )

    @on(Info)
    def log_info(self, msg: Info):
        self.wlog.info(f"{msg.func:>15}:{msg.msg}")
        return

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


if __name__ == "__main__":
    ke_app = KEApp()
    ke_app.run()
