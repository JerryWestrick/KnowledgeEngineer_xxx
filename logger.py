from textual.widgets import RichLog


class Logger:
    logger_widget: RichLog | None = None
    def msg(self, step, msg: dict):
        hcolor = 'green'
        if msg['role'] == 'assistant':
            hcolor = 'deep_sky_blue1'

        role = msg['role']
        hrole = f"({role:9})"
        content = [f"{msg['content']}"]

        step_id = f"{step.pname}/{step.name} {step.interaction_no:02}"
        head = f"[{hcolor}]{self.namespace:>10}::{step_id:}[/{hcolor}]:"

        if role == 'system':
            self.logger_widget.write(f"{head}message{hrole}{content}")
        elif role == 'user':
            self.logger_widget.write(f"{head}message{hrole}{content}")
        elif role == 'function':
            self.logger_widget.write(f"{head}{msg['name']}{hrole}{content}")
        elif role == 'assistant':
            if 'function_call' in msg.keys():
                self.logger_widget.write(f"{head}{msg['function_call']['name']}{hrole}{[msg['function_call']['arguments']]}")
            else:
                self.logger_widget.write(f"{head}message{hrole}{content}")
        else:
            self.logger_widget.write(f"[red]{step_id:>55}[\\red]::<<<<<<<<<<< UNKNOWN ROLE")
            self.logger_widget.write(f"[red]{step_id:>55}[\\red]::{content}")

    def __init__(self, namespace: str, debug: bool = True):
        self.namespace = namespace
        self.debug = debug

    def error(self, msg: str):
        self.logger_widget.write(f"[on red]{self.namespace:>10}[/on red]::{msg}",)

    def warn(self, msg: str):
        self.logger_widget.write(f"[bold orange]{self.namespace:>10}::{msg}[/bold orange]")

    def info(self, msg: str):
        if self.debug:
            self.logger_widget.write(f"{self.namespace:>10}::{msg}")
