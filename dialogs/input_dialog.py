"""Provides a dialog for getting a yes/no response from the user."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Label, Input


class Input_Dialog(ModalScreen[str]):
    """A dialog for asking a user for a string."""

    CSS_PATH = "input_dialog.tcss"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "", show=False),
    ]
    """Bindings for the input dialog."""

    def __init__(  # pylint:disable=too-many-arguments
        self,
        title: str,
        question: str,
        offset: tuple[int, int],
    ) -> None:
        """Initialise the Input dialog.

        Args:
            requester: The widget requesting the input.
            title: The title for the dialog.
            question: The question to ask.
            id: The ID for the dialog.
        """
        super().__init__()
        self._title = title
        """The title for the dialog."""
        self._question = question
        """The question to ask the user."""
        self._offset = offset

    def compose(self) -> ComposeResult:
        """Compose the content of the dialog."""
        with Horizontal(id="id_horizontal"):
            yield Label(self._question)
            yield Input("")

    def on_mount(self) -> None:
        """Configure the dialog once the DOM is ready."""
        h = self.query_one("#id_horizontal")
        h.border_title = self._title
        h.styles.offset = self._offset
        self.query_one(Input).focus()


    @on(Input.Submitted)
    def send_response(self, event: Input.Submitted) -> None:
        """ Input was given

        Args:
            event: The event to handle.
        """
        self.dismiss(event.value)
