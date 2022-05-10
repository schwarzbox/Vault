# vault.py

from rich.align import Align
from rich.box import HEAVY
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

from textual.reactive import Reactive


class ButtonMixin:
    clicked: Reactive[RenderableType] = Reactive(False)
    mouse_over: Reactive[RenderableType] = Reactive(False)
    height = None

    def render(self) -> Panel:
        renderable = Align.center(
            Text(
                self.on_click_label if self.clicked else self.label,
            ),
            vertical='middle',
            style='yellow' if self.clicked else 'green'
        )
        return Panel(
            renderable,
            title=self.title,
            title_align='left',
            height=self.height,
            border_style=Style(
                color='yellow' if self.mouse_over else 'green'
            ),
            box=HEAVY
        )

    def on_click(self) -> None:
        self.clicked = True

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False
        self.clicked = False
