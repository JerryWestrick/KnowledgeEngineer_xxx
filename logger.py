import json

from pydantic_core import from_json
from textual.widgets import RichLog


class Logger:
    logger_widget: RichLog | None = None

    top_left = '╭──'
    top_right = '─╮'
    bottom_left = '╰──'
    bottom_right = '──╯'



    def start_step(self, step):
        head = f"[green]{self.namespace:>10}::[/][white]│ [/]"
        self.logger_widget.write(f"{head}[green]{self.top_left}{'─' * 80}[/]")

    def stop_step(self, step):
        head = f"[green]{self.namespace:>10}::[/][white]│ [/]"
        self.logger_widget.write(f"{head}[green]{self.bottom_left}{'─' * 80}[/]")

    def umsg(self, step, msg: dict):
        content = [f"{msg['content']}"]
        head = f"[green]{self.namespace:>10}::[/][white]│ [/][green]│ [/]"
        self.logger_widget.write(f"{head}[medium_orchid]{msg['role'] + ' message':>14}[/]:[green]{content}[/]")

    def ai_msg(self, step, msg: dict):
        hcolor = 'deep_sky_blue1'
        role = msg['role']
        hrole = f"({role:9})"
        content = [f"{msg['content']}"]

        head = f"[green]{self.namespace:>10}::[/][white]│ [/][green]│ [/]"

        if 'function_call' in msg.keys():
            arg_str = msg['function_call']['arguments']
            args = json.loads(arg_str)
            fn = f"[deep_sky_blue1]{msg['function_call']['name']}[/]"
            if fn == 'read_file':
                self.logger_widget.write(f"{head}       {fn}({args['name']})")
            else:
                self.logger_widget.write(f"{head}       {fn}({args['name']}, ...)[green]{[arg_str]}[/]")
        else:
            self.logger_widget.write(f"{head}[deep_sky_blue1]{'AI message':>14}[/]:[green]{content}[/]")

    def ret_msg(self, step, msg: dict):
        hcolor = 'green'
        role = msg['role']
        hrole = f"({role:9})"
        content = [f"{msg['content']}"]

        head = f"[green]{self.namespace:>10}::[/][white]│ [/][green]│ [/]"

        self.logger_widget.write(f"{head}           [medium_orchid]rtn[/]:[green]{content}[/]")

    def __init__(self, namespace: str, debug: bool = True):
        self.namespace = namespace
        self.debug = debug

    def error(self, msg: str):
        self.logger_widget.write(f"[on red]{self.namespace:>10}[/on red]::{msg}", )

    def warn(self, msg: str):
        self.logger_widget.write(f"[bold orange]{self.namespace:>10}::{msg}[/bold orange]")

    def info(self, msg: str):
        if self.debug:
            self.logger_widget.write(f"{self.namespace:>10}::{msg}")
