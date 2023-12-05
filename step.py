# The name of the step is the key to the dictionary

import json
import time

from textual.widgets import RichLog

from ai import AI
from db import DB
from logger import Logger


class Step:
    log = Logger(namespace="Step")
    memory = DB('Memory')

    def __init__(self,
                 name: str,
                 prompt_name: str,
                 ai: AI,
                 verify_prompt: str = '',
                 storage_path: str = '',
                 text_file: str = '',
                 file_process_enabled: bool = False,
                 file_process_name: str = '',
                 file_glob: str = '',
                 macros: dict[str, str] = None):
        self.name: str = name
        self.prompt_name: str = prompt_name
        self.verify_prompt: str = verify_prompt
        self.storage_path: str = storage_path
        self.text_file: str = text_file
        self.file_process_enabled: bool = file_process_enabled
        self.file_process_name: str = file_process_name
        self.file_glob: str = file_glob
        self.macros: dict[str, str] = macros
        if macros is None:
            self.macros = {}
        self.ai: AI = ai

    def to_json(self) -> dict:
        """
        Convert the Step to a JSON object
        """
        return {
            'name': self.name,
            'prompt_name': self.prompt_name,
            'verify_prompt': self.verify_prompt,
            'storage_path': self.storage_path,
            'text_file': self.text_file,
            'file_process_enabled': self.file_process_enabled,
            'file_process_name': self.file_process_name,
            'file_glob': self.file_glob,
            'macros': self.macros,
            'ai': self.ai.to_json()
        }

    @classmethod
    def from_json(cls, json_obj: dict) -> 'Step':
        """
        Create a Step from a JSON object
        """
        step = cls(
            name=json_obj['name'],
            prompt_name=json_obj['prompt_name'],
            verify_prompt=json_obj['verify_prompt'],
            storage_path=json_obj['storage_path'],
            text_file=json_obj['text_file'],
            file_process_enabled=json_obj['file_process_enabled'],
            file_process_name=json_obj['file_process_name'],
            file_glob=json_obj['file_glob'],
            macros=json_obj['macros'],
            ai=AI.from_json(json_obj['ai'])
        )
        return step

    def update_gui(self):
        # Send Update to the GUI
        # msg = {'cmd': 'update', 'cb': 'update_step', 'rc': 'Okay', 'object': 'step', 'record': self.to_json()}
        # response = json.dumps(msg, ensure_ascii=False, default=str)
        # self.log.info(f"Update GUI called with {msg}")
        pass

    async def run(self, pname):
        self.pname = pname          # Add name of process to step...
        self.interaction_no = 0     # start count of interactions with AI
        msg = {}
        msgs = []
        start_time = time.time()
        head_len = 12
        head = ' ' * head_len
        self.memory.macro = self.macros  # Use these values for macro substitution
        try:
            messages = self.memory[self.prompt_name]
        except Exception as err:
            self.log.error(f"Error in self.memory[self.prompt_name] {err}")
            raise

        # Clear Old History
        # self.log.info("step.run()::1")
        self.ai.answer = ''
        self.ai.messages = []
        self.ai.files = {}
        self.ai.e_stats['elapsed_time'] = 0.0
        self.ai.e_stats['prompt_tokens'] = 0.0
        self.ai.e_stats['completion_tokens'] = 0.0
        self.ai.e_stats['sp_cost'] = 0.0
        self.ai.e_stats['sc_cost'] = 0.0
        self.ai.e_stats['s_total'] = 0.0
        self.ai.e_stats['elapsed_time'] = 0.0

        top_left = '╭─ '
        top_right = '─╮'
        bottom_left = '╰──'
        bottom_right = '──╯'

        txt = f'{top_left}Step: {self.pname}:{self.name} -- {self.prompt_name}'
        self.log.info(f"{txt}")
        self.log.info(f"│ Model: {self.ai.model}, Temperature: {self.ai.temperature}, Max Tokens: {self.ai.max_tokens:,}")


        try:
            # self.ai.messages = messages
            self.update_gui()
            ai_response = await self.ai.generate(self, messages)
        except Exception as err:
            self.log.error(f"Error in ai.generate: {err}")
            raise

        self.update_gui()

        # Write log file if required...
        if self.text_file != '':
            full_path = f"{self.storage_path}/{self.text_file}"
            self.memory[full_path] = self.ai.answer
            self.log.info(f"│ Writing {full_path}")


        total_tokens= (int(self.ai.e_stats['prompt_tokens']) + int(self.ai.e_stats['completion_tokens']))
        self.ai.e_stats['total_tokens'] = total_tokens
        if total_tokens > int(self.ai.max_tokens):
            wcolor = "dark_orange3"
        else:
            wcolor = "green"

        self.ai.e_stats['elapsed_time'] = time.time() - start_time
        mins, secs = divmod(self.ai.e_stats['elapsed_time'], 60)


        self.log.info(f"│ Elapsed: {int(mins)}m {secs:.2f}s Token Usage: "
                      f"Total: [{wcolor}]{total_tokens:,}[/] ("
                      f"Prompt: {int(self.ai.e_stats['prompt_tokens']):,}, "
                      f"Completion: {int(self.ai.e_stats['completion_tokens']):,})"
                      f"\n{head}"
                      f"│ Costs:: Total: ${self.ai.e_stats['s_total']:.2f} "
                      f"(Prompt: ${self.ai.e_stats['sp_cost']:.4f}, "
                      f"Completion: ${self.ai.e_stats['sc_cost']:.4f})"
                      f"\n{head}{bottom_left}{'─'*80}")
