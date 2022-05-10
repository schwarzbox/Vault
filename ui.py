# vault.py
import os

import pyperclip as pc

from rich.align import Align
from rich.box import HEAVY
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

from textual.app import App
from textual.reactive import Reactive
from textual.views import GridView
from textual.widget import Widget
from textual.widgets import (
    Button, Footer, ScrollView, TreeClick, TreeControl
)

import errors as err

from mixins import ButtonMixin

from settings import VAULT_DIR


class CellGrid(GridView):
    def __init__(self, *args, cells, **kwargs):
        super().__init__(*args, **kwargs)
        self.cells = cells

    async def on_mount(self) -> None:
        self.grid.add_column('col', fraction=1, max_size=24)
        self.grid.add_row('row', fraction=1, max_size=3)
        self.grid.set_repeat(True, True)
        self.grid.set_align('center', 'center')
        self.update_cells(self.cells)

    def update_cells(self, cells) -> None:
        self.grid.widgets.clear()
        self.grid.place(*cells)
        self.refresh()


class CellButton(ButtonMixin, Button):
    def __init__(self, *args, encoder, title, value, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoder = encoder
        self.title = self.encoder.decode(title)
        self.label = self.encoder.decode(self.label)
        self.value = value
        self.on_click_label = '🔑'

    def on_click(self) -> None:
        super().on_click()
        pc.copy(self.encoder.decode(self.value))


class CopyButton(ButtonMixin, Button):
    def __init__(self, *args, title, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.on_click_label = '✏️'
        self.action = None

    def hide(self):
        self.visible = False

    def on_click(self) -> None:
        super().on_click()
        if self.action:
            loc = self.action()
            pc.copy(loc)
        self.set_timer(1.2, lambda: self.hide())


class Notification(Widget):
    def __init__(self, title: str, label: str):
        super().__init__(title)
        self.visible = False
        self.title = title
        self.label = label

    def render(self) -> Panel:
        return Panel(
            Align.center(
                Text(self.label),
                vertical='middle',
                style='green'
            ),
            title=self.title,
            title_align='left',
            border_style=Style(
                color='green'
            ),
            box=HEAVY
        )

    def hide(self):
        self.visible = False

    def show(self, title, label):
        self.title = title
        self.label = label
        self.visible = True
        self.set_timer(2, lambda: self.hide())


class LoadTree(TreeControl):
    async def update_dirs(self, cwd='.'):
        for folder in os.listdir(cwd):
            if '.json' in folder:
                await self.add(
                    self.root.id,
                    folder,
                    {'path': folder}
                )
            elif os.path.isdir(folder):
                await self.add(
                    self.root.id,
                    folder,
                    {'dir': folder}
                )
        self.refresh(layout=True)


class ViewApp(App):
    show_cell: Reactive[RenderableType] = Reactive(True)
    show_dump: Reactive[RenderableType] = Reactive(False)
    show_load: Reactive[RenderableType] = Reactive(False)
    show_find: Reactive[RenderableType] = Reactive(False)

    def __init__(self, *args, vlt, **kwargs):
        super().__init__(*args, **kwargs)
        self.vlt = vlt

    def watch_show_cell(self, show_edit: bool) -> None:
        self.cells.visible = self.show_cell

    def watch_show_dump(self, show_edit: bool) -> None:
        self.dump_json.visible = self.show_dump

    def watch_show_load(self, show_edit: bool) -> None:
        self.load_json.visible = self.show_load

    def watch_show_find(self, show_edit: bool) -> None:
        self.find_db.visible = self.show_find

    def action_dump_data(self):
        loc = self.vlt.get_json_path()
        self.dump_json.label = os.path.basename(loc)
        self.dump_json.action = lambda: self.vlt.dump_data(
            loc, verbose=False
        )

        self.dump_json.visible = not self.dump_json.visible
        self.show_load = False
        self.show_find = False
        self.show_cell = True

        self.notification.visible = False

    def action_load_data(self):
        self.show_load = not self.show_load
        self.show_dump = False
        self.show_find = False
        self.show_cell = not self.show_load

        self.notification.visible = False

    def action_find_database(self):
        self.find_db.label = VAULT_DIR
        self.find_db.action = lambda: self.vlt.find_database(
            verbose=False
        )

        self.find_db.visible = not self.find_db.visible
        self.show_dump = False
        self.show_load = False
        self.show_cell = True

        self.notification.visible = False

    async def handle_tree_click(
        self, message: TreeClick[dict]
    ) -> None:

        path = message.node.data.get('path', None)
        directory = message.node.data.get('dir', None)

        if path:
            title = f'Load {self.vlt.name}'
            try:
                loc = self.vlt.load_data(path, verbose=False)
                self.cells.update_cells(
                    cells=self._create_cells()
                )
                label = os.path.basename(loc)
                self.action_load_data()

            except (err.FileNotFound, err.InvalidJSON) as e:
                title = 'Error'
                label = str(e)

            self.notification.show(title, label)
        elif directory:
            down = os.path.abspath(directory)
            os.chdir(down)
            await self._create_tree(down)
        else:
            up = os.path.abspath(
                os.path.join(message.node.label, '../')
            )
            os.chdir(up)
            await self._create_tree(up)

    async def _create_tree(self, path):
        tree = LoadTree(path, {})
        await tree.update_dirs(path)
        await tree.root.expand()
        await self.load_json.update(tree)

    def _create_cells(self):
        instances = []
        for folder in self.vlt.vault:
            for key in self.vlt.vault[folder]:
                data = self.vlt.vault.get(folder, {})
                instances.append(
                    CellButton(
                        encoder=self.vlt.encoder,
                        title=folder,
                        label=key,
                        value=data.get(key),
                        name='cell',
                    )
                )
        return instances

    async def on_load(self) -> None:
        await self.bind('ctrl+q', 'quit', '✕')
        await self.bind('ctrl+d', 'dump_data', 'Dump JSON')
        await self.bind('ctrl+l', 'load_data', 'Load JSON')
        await self.bind('ctrl+f', 'find_database', 'Find DB')

    async def on_mount(self) -> None:
        await self.view.dock(Footer(), edge='bottom', z=2)

        self.cells = CellGrid(cells=self._create_cells())
        self.cells.visible = self.show_cell

        self.notification = Notification(
            title='', label='',
        )

        self.dump_json = CopyButton(
            title=f'Dump {self.vlt.name}', label=''
        )
        self.dump_json.visible = self.show_dump

        self.load_json = ScrollView()
        self.load_json.visible = self.show_load

        self.find_db = CopyButton(
            title=f'Find {self.vlt.name} DB', label=''
        )
        self.find_db.visible = self.show_find

        await self._create_tree(os.getcwd())

        await self.view.dock(self.notification, z=2)
        await self.view.dock(self.dump_json, z=2)
        await self.view.dock(self.load_json, z=2)
        await self.view.dock(self.find_db, z=2)
        await self.view.dock(self.cells, z=1)
