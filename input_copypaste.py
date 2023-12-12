from textual import on
from textual.events import MouseDown, Key
from textual.widgets import Input


class InputCP(Input):

    @on(MouseDown)
    def check_event(self, event: MouseDown):
        if event.ctrl:
            if event.button == 1:
                self.set_clipboard()
                event.stop()
            elif event.button == 3:
                self.get_clipboard()
                event.stop()

    @on(Key)
    def check_key_event(self, event: Key):
        if event.key == 'ctrl+o':
            self.set_clipboard()
            event.stop()
        elif event.key == 'ctrl+p':
            self.get_clipboard()
            event.stop()

    def set_clipboard(self):
        self.app.clipboard = {"text": self.value}

    def get_clipboard(self):
        if 'text' in self.app.clipboard:
            self.value = self.app.clipboard['text']


