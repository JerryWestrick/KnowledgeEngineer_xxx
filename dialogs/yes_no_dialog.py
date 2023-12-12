"""Provides a dialog for getting a yes/no response from the user."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class YesNoDialog(ModalScreen[bool]):
    """A dialog for asking a user a yes/no question."""

    CSS_PATH = "yes_no_dialog.tcss"

    BINDINGS = [
        Binding("left,up", "focus_previous", "", show=False),
        Binding("right,down", "focus_next", "", show=False),
        Binding("escape", "app.pop_screen", "", show=False),
    ]
    """Bindings for the yes/no dialog."""

    def __init__(  # pylint:disable=too-many-arguments
        self,
        title: str,
        question: str,
        yes_label: str = "Yes",
        no_label: str = "No",
        yes_first: bool = True,
    ) -> None:
        """Initialise the yes/no dialog.

        Args:
            requester: The widget requesting the input.
            title: The title for the dialog.
            question: The question to ask.
            yes_label: The optional label for the yes button.
            no_label: The optional label for the no button.
            yes_first: Should the yes button come first?
            cargo: Any cargo value for the question.
            id: The ID for the dialog.
        """
        super().__init__()
        self._title = title
        """The title for the dialog."""
        self._question = question
        """The question to ask the user."""
        self._aye = yes_label
        """The label for the yes button."""
        self._naw = no_label
        """The label for the no button."""
        self._aye_first = yes_first
        """Should the positive button come first?"""

    def compose(self) -> ComposeResult:
        """Compose the content of the dialog."""
        with Vertical():
            yield Static(self._question, id="question", classes="spaced")
            with Horizontal(id="buttons"):
                aye = Button(self._aye, id="yes", classes="small_btn")
                naw = Button(self._naw, id="no", classes="small_btn")
                if self._aye_first:
                    aye.variant = "primary"
                    yield aye
                    yield naw
                else:
                    naw.variant = "primary"
                    yield naw
                    yield aye

    def on_mount(self) -> None:
        """Configure the dialog once the DOM is ready."""
        self.query_one("YesNoDialog > Vertical").border_title = self._title
        self.query(Button).first().focus()


    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle a button being pressed on the dialog.

        Args:
            event: The event to handle.
        """
        self.dismiss(event.button.id == "yes")