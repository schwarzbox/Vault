# vault.py
import os
from typing import TypeVar

import pyperclip as pc

from rich.align import Align
from rich.box import HEAVY
from rich.color import Color
from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.text import Text


from textual.app import App
from textual.scrollbar import ScrollBar, ScrollBarRender
from textual.views import GridView
from textual.widget import Widget
from textual.widgets import (
    Button, Footer, ScrollView, TreeClick, TreeControl, TreeNode
)

import errors as err

from mixins import ButtonMixin

from settings import BRIGHT_GREEN, GRAY, GREEN, VAULT_DIR, YELLOW

console = Console()
NodeDataType = TypeVar('NodeDataType')


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
                style=BRIGHT_GREEN
            ),
            title=self.title,
            title_align='left',
            border_style=Style(color=GREEN),
            box=HEAVY
        )

    def hide(self):
        self.visible = False

    def show(self, title, label):
        self.title = title
        self.label = label
        self.visible = True
        self.set_timer(2, lambda: self.hide())


class LoadScroll(ScrollBar):
    def render(self) -> RenderableType:
        style = Style(
            bgcolor=Color.parse(GRAY),
            color=Color.parse(YELLOW if self.grabbed else GREEN),
        )
        return ScrollBarRender(
            virtual_size=self.virtual_size,
            window_size=self.window_size,
            position=self.position,
            vertical=self.vertical,
            style=style,
        )


class LoadTree(TreeControl):
    async def update_dirs(self, cwd='.'):
        for folder in os.listdir(cwd):
            if folder.startswith('.'):
                continue
            if os.path.isdir(folder):
                await self.add(
                    self.root.id,
                    folder,
                    {'dir': folder}
                )
            else:
                await self.add(
                    self.root.id,
                    folder,
                    {'path': folder}
                )

        self.refresh(layout=True)

    def render_node(
        self, node: TreeNode[NodeDataType]
    ) -> RenderableType:

        color = GRAY
        is_clickable = False
        if os.path.isdir(node.label):
            color = BRIGHT_GREEN
            is_clickable = True
        elif os.path.splitext(node.label)[1] == '.json':
            color = YELLOW
            is_clickable = True

        label = (
            Text(
                node.label,
                no_wrap=True,
                style=color,
                overflow='ellipsis'
            )
            if isinstance(node.label, str)
            else node.label
        )
        if is_clickable:
            if node.id == self.hover_node:
                label.stylize('underline')

            label.apply_meta(
                {
                    '@click': f'click_label({node.id})',
                    'tree_node': node.id
                }
            )
        return label


class ViewApp(App):
    def __init__(self, *args, vlt, **kwargs):
        super().__init__(*args, **kwargs)
        self.vlt = vlt

    def action_dump_data(self):
        loc = self.vlt.get_json_path()
        self.dump_json.label = os.path.basename(loc)
        self.dump_json.action = lambda: self.vlt.dump_data(
            loc, verbose=False
        )

        self.dump_json.visible = not self.dump_json.visible
        self.load_json.visible = False
        self.find_db.visible = False
        self.cells.visible = True

        self.notification.visible = False

    def action_load_data(self):
        self.load_json.visible = not self.load_json.visible
        self.dump_json.visible = False
        self.find_db.visible = False
        self.cells.visible = not self.load_json.visible

        self.notification.visible = False

    def action_find_database(self):
        self.find_db.label = VAULT_DIR
        self.find_db.action = lambda: self.vlt.find_database(
            verbose=False
        )

        self.find_db.visible = not self.find_db.visible
        self.dump_json.visible = False
        self.load_json.visible = False
        self.cells.visible = True

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
        self.cells.visible = True

        self.notification = Notification(
            title='', label='',
        )

        self.dump_json = CopyButton(
            title=f'Dump {self.vlt.name}', label=''
        )
        self.dump_json.visible = False

        self.load_json = ScrollView()
        self.load_json.vscroll = LoadScroll(vertical=True)
        self.load_json.hscroll = LoadScroll(vertical=False)
        self.load_json.visible = False

        self.find_db = CopyButton(
            title=f'Find {self.vlt.name} DB', label=''
        )
        self.find_db.visible = False

        await self._create_tree(os.getcwd())

        await self.view.dock(self.notification, z=2)
        await self.view.dock(self.dump_json, z=2)
        await self.view.dock(self.load_json, z=2)
        await self.view.dock(self.find_db, z=2)
        await self.view.dock(self.cells, z=1)
