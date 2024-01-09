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
from processes import ProcessList, ProcessList_save
from step import Step
from step_editor import StepEditor

from dialogs.inputdialog import InputDialog


class ProcessEditor(Static):
    wlog = Logger(namespace="ProcessEditor", debug=False)
    plog = Logger(namespace="Process", debug=True)
    selected_node: TreeNode | None = None
    selected_process: str = ''
    selected_step: str = ''
    last_pos: (int, int) = (0, 0)

    def compose(self) -> ComposeResult:
        self.process_tree: Tree[dict] = Tree("Processes")
        self.process_tree.root.expand()
        self.process_tree.show_root = False
        for proc_name in ProcessList.keys():
            procedure = self.process_tree.root.add(proc_name)
            for step in ProcessList[proc_name]:
                procedure.add_leaf(step.name, data=step)
        self.border_title = 'Process List'
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
        if len(e.node.children) == 0:
            # Process a Step
            if e.node.data:
                self.wlog.info(f"Selected: {e.node.data.prompt_name}|{e.node.parent.label}|{e.node.label}")
                self.selected_process = str(e.node.parent.label)
                self.selected_step = str(e.node.label)
                self.post_message(StepEditor.StepAction("Select", e.node.parent.label, e.node.label))
        else:
            self.selected_process = str(e.node.label)
            self.selected_step = ""

    def get_step_no(self, process_name: str, step_name: str) -> int:
        pos: int = 0
        for s in ProcessList[process_name]:
            if s.name == step_name:
                break
            pos += 1
        return pos

    @work
    async def do_popup_menu(self, event: MouseDown) -> None:
        screen_pos = (event.screen_x, event.screen_y)
        if self.selected_step:
            step_cmd = await self.app.push_screen_wait(
                PopUpMenu(
                    f"Step PopUp: {self.selected_step}",
                    ['New Step', f'New Step After "{self.selected_step}"', f'Delete Step "{self.selected_step}"'],
                    offset=screen_pos
                )
            )
            self.wlog.info(f"Got '{step_cmd}' from Step PopUp")
            keywords = str(step_cmd).split(' ')
            self.wlog.info(f"keywords {keywords}")
            match keywords[0]:
                case "New":
                    pos = 0
                    if len(keywords) > 2 and keywords[2] == "After":
                        pos = self.get_step_no(self.selected_process, self.selected_step) + 1
                    ProcessList[self.selected_process].insert(pos, Step('New Step', ai=AI()))
                    ProcessList_save(ProcessList)
                    father = self.selected_node.parent
                    father.remove_children()
                    for s in ProcessList[self.selected_process]:
                        father.add_leaf(s.name, s)
                    return

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

                    pos = self.get_step_no(self.selected_process, self.selected_step)
                    ProcessList[self.selected_process].pop(pos)
                    ProcessList_save(ProcessList)
                    self.selected_node.remove()
                    self.selected_step = ''
                    self.selected_node = None
                    return

        elif self.selected_process:
            menu_cmd = await self.app.push_screen_wait(
                PopUpMenu(f"Process Popup : {self.selected_process}",
                          ['New Process',
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
                    new_step = Step("Dummy Step", ai=AI())
                    ProcessList[new_name] = [new_step]
                    procedure = self.process_tree.root.add(new_name)
                    procedure.add_leaf(new_step.name, data=new_step)
                    ProcessList_save(ProcessList)
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

                    if self.selected_process in ProcessList.keys():
                        del ProcessList[self.selected_process]
                        self.selected_node.remove()
                        self.selected_node = None
                        self.selected_process = ""
                        self.selected_step = ""
                        ProcessList_save(ProcessList)
                    return

                case "Execute":
                    self.execute_process(self.selected_process)
                    return

                case "_":
                    self.wlog.error(f"Invalid menu return: {str(menu_cmd)}... \nExpected one of [New, Delete, Execute]")
                    return

    @work
    async def execute_process(self, process_name: str):
        self.selected_process = process_name
        self.plog.info(f"Begin Execution of Process {self.selected_process}")
        step_no = 1
        start_time = time.time()
        e_stats = {}
        for step in ProcessList[self.selected_process]:
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
