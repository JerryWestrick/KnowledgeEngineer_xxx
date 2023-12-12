from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Button

from logger import Logger


class PopUpMenu(ModalScreen[str]):
    """A dialog for asking a user to select one of several options."""

    wlog: Logger = Logger(namespace="PopUpMenu", debug=True)

    CSS_PATH = ("popup_menu.tcss")

    BINDINGS = [
        Binding("left,up", "focus_previous", "", show=False),
        Binding("right,down", "focus_next", "", show=False),
        Binding("escape", "app.pop_screen", "", show=False),
    ]
    """Bindings for the popup menu dialog."""

    def __init__(
        self,
        title: str,
        options: [str],
        offset: tuple[int, int],

    ) -> None:
        """Initialise the popup menu.

        Args:
            requester: The widget requesting the input.
            title: The title for the menu.
            id: The ID for the dialog.
            options: dict[str, dict]
        """
        super().__init__()
        self._title = title
        """The title for the dialog."""
        self._options = options
        """The question to ask the user."""
        self._offset = offset
        """The position of the popup"""

    def compose(self) -> ComposeResult:
        """Compose the content of the dialog."""
        with Vertical(id="popup_vertical"):
            for option in self._options:
                yield Button(label=option)
        self.wlog.info("End Compose")

    def on_mount(self) -> None:
        """Configure the dialog once the DOM is ready."""
        v = self.query_one("Vertical")
        v.border_title = self._title
        v.styles.min_width = f"{max(len(self._title) + 6, 17)}"
        v.styles.offset = self._offset
        self.query(Button).first().focus()
        self.wlog.info("End on_mount")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle a button being pressed on the dialog.

        Args:
            event: The event to handle.
        """
        self.wlog.info("Begin on_button_pressed")
        self.dismiss(event.button.label)

