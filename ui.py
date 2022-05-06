# vault.py

import pyperclip as pc

from rich.align import Align
from rich.box import HEAVY
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

from textual.app import App
from textual.reactive import Reactive
from textual.widgets import Button, Footer


class Cell(Button):
    clicked = Reactive(False)
    mouse_over = Reactive(False)

    def __init__(self, *args, encoder, title, value,  **kwargs):
        super().__init__(*args, **kwargs)
        self.encoder = encoder
        self.title = self.encoder.decode(title)
        self.label = self.encoder.decode(self.label)
        self.value = value

    def on_click(self) -> None:
        self.clicked = True
        pc.copy(self.encoder.decode(self.value))

    def render(self) -> Panel:
        renderable = Align.center(
            Text(
                '🔑' if self.clicked else self.label
            )
        )
        return Panel(
            renderable,
            title=self.title,
            title_align='left',
            border_style=Style(
                color='yellow' if self.mouse_over else 'green'
            ),
            box=HEAVY
        )

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False
        self.clicked = False


class ViewApp(App):
    reset_path: Reactive[RenderableType] = Reactive(False)

    def __init__(self, *args, vlt, **kwargs):
        super().__init__(*args, **kwargs)
        self.vlt = vlt

    def action_dump_data(self):
        self.vlt.dump_data(verbose=False)

    async def on_load(self) -> None:
        await self.bind('ctrl+q', 'quit', '❎')
        await self.bind('ctrl+d', 'dump_data', 'Dump JSON')

    async def on_mount(self) -> None:
        await self.view.dock(Footer(), edge='bottom')

        instances = []
        for folder in self.vlt.vault:
            for key in self.vlt.vault[folder]:
                data = self.vlt.get_folder(folder)
                instances.append(
                    Cell(
                        encoder=self.vlt.encoder,
                        title=folder,
                        label=key,
                        value=data.get(key),
                        name='cell',
                    )
                )

        grid = await self.view.dock_grid()

        grid.add_column('col', fraction=1, max_size=24)
        grid.add_row('row', fraction=1, max_size=3)
        grid.set_repeat(True, True)
        grid.set_align('center', 'center')
        grid.place(*instances)
