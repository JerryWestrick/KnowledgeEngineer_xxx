import argparse

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.events import Key
from textual.widgets import Header, Footer, RichLog

from memory_tree import MemoryTree, DirTree
from file_editor import FileEditor
from logger import Logger
from process_commands import ProcessCommands, ProcessCommand
from process_editor import ProcessEditor
from step_editor import StepEditor


class KEApp(App):
    wlog = Logger(namespace="KEApp", debug=False)
    BINDINGS = [
        ('d', 'toggle_dark', "Toggle dark mode"),
        ('q', 'quit', "Quit Application"),
        ('l', 'toggle_log', "Toggle log / gui mode")
    ]
    TITLE = "Knowledge Engineer"
    SUB_TITLE = "AI Prompt Memory Engineering Tool"

    CSS_PATH = "ke.tcss"

    COMMANDS = App.COMMANDS | {ProcessCommands}
    clipboard: dict[str, str] = {}

    # pe_language = get_language("PromptEngineer")

    def __init__(self,
                 driver_class=None,
                 css_path=None,
                 watch_css=False,
                 arguments: argparse.Namespace = None
                 ):
        super().__init__(
            driver_class=driver_class,
            css_path=css_path,
            watch_css=watch_css,
        )
        self.args = arguments
        self.log_mode = False

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
            id="main_grid", classes="main_grid"
        )
        yield self.grid
        yield self.rt_log

        self.log_mode = False
        self.wlog.info(f"Processes Loaded")

    def set_log_mode(self) -> None:
        self.log_mode = True
        self.grid.styles.display = 'none'
        self.wlog.info(f"Switched to Log Mode")

    def set_gui_mode(self):
        self.log_mode = False
        self.grid.styles.display = 'block'
        self.wlog.info(f"Switched to Gui Mode")

    @on(Key)
    def check_key_event(self, event: Key):
        match event.key:
            case 'ctrl+up':
                height = int(str(self.rt_log.styles.height)[:-2])
                self.rt_log.styles.height = f"{height + 1}fr"

            case 'ctrl+down':
                height = int(str(self.rt_log.styles.height)[:-2])
                if height > 2:
                    self.rt_log.styles.height = f"{height - 1}fr"

            case 'ctrl+l':
                self.set_log_mode()

            case 'ctrl+g':
                self.set_gui_mode()

            case _:
                self.wlog.info(f"{event}")

    @on(ProcessCommand)
    def on_process_command(self, cmd: ProcessCommand) -> None:
        self.wlog.info(f"on_process_command({cmd})")
        match cmd.object_type:
            case "Process":
                self.process_editor.execute_process(cmd.object_name)

            case "Step":
                pname, sname = cmd.object_name.split('/')
                self.post_message(StepEditor.StepAction("Execute", pname, sname))

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

    async def on_mount(self) -> None:
        if self.args.log:
            self.set_log_mode()

        if self.args.gui:
            self.set_gui_mode()

        if self.args.step:
            self.set_log_mode()
            self.on_process_command(
                ProcessCommand(command='Execute', object_type='Step', object_name=f"{self.args.proc}/{self.args.step}")
            )
        elif self.args.proc:
            self.set_log_mode()
            self.on_process_command(
                ProcessCommand(command='Execute', object_type='Process', object_name=self.args.proc)
            )


if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description="Knowledge Engineering: AI Prompt Memory Engineering Tool")
    # Add the arguments
    parser.add_argument("-gui", action="store_true", help="activate GUI")
    parser.add_argument("-log", action="store_true", help="activate Log Mode")
    parser.add_argument("-proc", metavar="proc-name", type=str, help="execute the given process name")
    parser.add_argument("-step", metavar="step-name", type=str, help="execute the given step in the proc")

    # Parse the arguments
    args: argparse.Namespace = parser.parse_args()

    # Now you can access the arguments as follows
    if not args.gui and not args.log and not args.proc:
        print("No Option chosen.")
        parser.print_help()
        exit(1)

    ke_app = KEApp(arguments=args)
    ke_app.run()
