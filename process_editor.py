from textual.app import ComposeResult
from textual.widgets import Static, Tree

from logger import Logger
from messages import StepAction
from processes import ProcessList


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


