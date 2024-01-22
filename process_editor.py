import time

from textual import on, work
from textual.app import ComposeResult
from textual.events import MouseDown
from textual.widgets import Static, Tree
from textual.widgets._tree import TreeNode

from ai import AI
from dialogs.popup_menu import PopUpMenu
from dialogs.yes_no_dialog import YesNoDialog
from logger import Logger
from processes import Processes
from step import Step
from step_editor import StepEditor

from dialogs.inputdialog import InputDialog


class ProcessEditor(Static):
    wlog = Logger(namespace="ProcessEditor", debug=False)
    plog = Logger(namespace="Process", debug=True)
    procs: Processes = Processes("Processes")
    selected_node: TreeNode | None = None
    selected_process: str = ''
    selected_step: str = ''
    last_pos: (int, int) = (0, 0)

    def compose(self) -> ComposeResult:
        self.process_tree: Tree[dict] = Tree("Processes")
        self.process_tree.root.expand()
        self.process_tree.show_root = False
        for proc_name in self.procs.glob_files("*"):
            procedure = self.process_tree.root.add(proc_name)
            step_names = self.procs.glob_files(f"{proc_name}/*")
            for step_name in step_names:
                step = self.procs[step_name]
                procedure.add_leaf(step.name, data=step)
        self.border_title = 'Process / Step'
        yield self.process_tree

    def node_id(self, proc: str | None = None, step: str | None = None) -> str:
        if proc is None:
            proc = self.selected_process
        if step is None:
            step = self.selected_step

            return f"<{proc}|{step}>"

    def on_tree_node_selected(self, e):
        e.prevent_default()
        self.wlog.info(f"Selected: {e.node.label} with {len(e.node.children)} children")
        self.selected_node = e.node
        if e.node.allow_expand:  # Process
            self.wlog.info(f"Selected Process: {e.node.label}")
            self.selected_process = str(e.node.label)
            self.selected_step = ""
        else:  # Step
            if e.node.data:
                self.wlog.info(f"Selected Step: {e.node.parent.label}/{e.node.label}")
                self.selected_process = str(e.node.parent.label)
                self.selected_step = str(e.node.label)
                self.post_message(StepEditor.StepAction("Select", e.node.parent.label, e.node.label))

    async def do_step_popup_menu(self, event: MouseDown) -> None:

        screen_pos = (event.screen_x, event.screen_y)
        step_cmd = await self.app.push_screen_wait(
            PopUpMenu(
                f"Step PopUp: {self.selected_step}",
                ['New Step', f'Delete Step "{self.selected_step}"'],
                offset=screen_pos
            )
        )
        self.wlog.info(f"Got '{step_cmd}' from Step PopUp")
        keywords = str(step_cmd).split(' ')
        self.wlog.info(f"keywords {keywords}")
        match keywords[0]:
            case "New":
                new_name = await self.app.push_screen_wait(
                    InputDialog("New Step Dialog", "Name of New Step:", offset=screen_pos)
                )
                if new_name:
                    step = Step(new_name, ai=AI())
                    self.procs[new_name] = step
                    self.selected_node.add_leaf(new_name, data=step)

            case "Delete":
                self.wlog.info(f"it is a Delete")
                confirmation: bool = await self.app.push_screen_wait(
                    YesNoDialog(f"Delete?",
                                f"Delete Step '{self.selected_step}'",
                                offset=screen_pos)
                )
                if not confirmation:
                    self.wlog.info(f"Delete not confirmed")
                    return

                del self.procs[f"{self.selected_process}/{self.selected_step}"]

    async def do_process_popup_menu(self, event: MouseDown) -> None:
        screen_pos = (event.screen_x, event.screen_y)
        menu_cmd = await self.app.push_screen_wait(
            PopUpMenu(f"Process Popup : {self.selected_process}",
                      [f'Create Step in "{self.selected_process}"',
                       'New Process',
                       f'Delete Process "{self.selected_process}"',
                       f'Execute Process "{self.selected_process}"'
                       ],
                      offset=screen_pos)
        )
        self.wlog.info(f"Process PopUp: {self.selected_process},  Step: {self.selected_step}>> {str(menu_cmd)}")
        keywords = str(menu_cmd).split(' ')
        match keywords[0]:
            case "New":
                self.wlog.info(f"PopUp New Process: {self.selected_process},  Step: {self.selected_step}")
                new_name = await self.app.push_screen_wait(
                    InputDialog("New Process Dialog", "Name of New process:", offset=screen_pos)
                )
                self.procs.new_process(new_name)
                self.process_tree.root.add(new_name)
                return

            case "Delete":
                self.wlog.info(f"it is a Delete")
                confirmation: bool = await self.app.push_screen_wait(
                    YesNoDialog(f"Delete?",
                                f"Delete Process '{self.selected_process}'",
                                offset=screen_pos)
                )
                if not confirmation:
                    self.wlog.info(f"Delete not confirmed")
                    return

                if self.selected_process in self.procs.glob_files('*'):
                    del self.procs[self.selected_process]
                    self.selected_node = None
                    self.selected_process = ""
                    self.selected_step = ""
                return

            case "Execute":
                self.execute_process(self.selected_process)
                return

            case "Create":
                # self.execute_process(self.selected_process)
                step_name = await self.app.push_screen_wait(
                    InputDialog("New Step Dialog", "Name of New step:", offset=screen_pos)
                )
                new_step = Step(name=step_name, ai=AI())
                self.procs[self.selected_process] = new_step
                self.selected_node.add_leaf(step_name, data=new_step)
                return

            case "_":
                self.wlog.error(f"Invalid menu return: {str(menu_cmd)}... \nExpected one of [Create, New, Delete, Execute]")
                return

    @work
    async def do_popup_menu(self, event: MouseDown) -> None:
        if self.selected_step:
            await self.do_step_popup_menu(event)
            return
        elif self.selected_process:
            await self.do_process_popup_menu(event)
            return

    @work
    async def execute_process(self, process_name: str):
        self.selected_process = process_name
        self.plog.info(f"Begin Execution of Process {self.selected_process}")
        step_no = 1
        start_time = time.time()
        e_stats = {}
        step_names = self.procs.glob_files(f"{self.selected_process}/*")
        for step_name in step_names:
            step = self.procs[step_name]
            self.plog.info(f"Execute {process_name}({step_no}): {step.name} ")
            await step.run(self.selected_process)
            for k, v in step.ai.e_stats.items():
                e_stats[k] = e_stats.get(k, 0.0) + v

            step_no += 1
        e_stats['elapsed_time'] = time.time() - start_time
        mins, secs = divmod(e_stats['elapsed_time'], 60)
        head_len = 12
        head = ' ' * head_len

        self.plog.info(f"Elapsed: {int(mins)}m {secs:.2f}s Token Usage: "
                       f"Total: [green]{e_stats['total_tokens']:,}[/] ("
                       f"Prompt: {int(e_stats['prompt_tokens']):,}, "
                       f"Completion: {int(e_stats['completion_tokens']):,})"
                       f"\n{head}"
                       f"Costs:: Total: [green]${e_stats['s_total']:.2f}[/] "
                       f"(Prompt: ${e_stats['sp_cost']:.4f}, "
                       f"Completion: ${e_stats['sc_cost']:.4f})"
                       )

    @on(MouseDown)
    async def check_event(self, event: MouseDown):
        self.wlog.info(f"MouseDown({event}")
        self.last_pos = (event.screen_x, event.screen_y)

        match event.button:
            case 1:
                if event.ctrl:
                    self.set_clipboard()
                    event.stop()

            case 3:
                self.do_popup_menu(event)
                event.stop()
