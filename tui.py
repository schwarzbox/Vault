# vault.py
import os

from rich.console import Console

from textual.app import App
from textual.widgets import Footer, ScrollView, TreeClick

import errors as err

from widgets import (
    CellGrid,
    CellButton,
    CopyButton,
    LoadTree,
    LoadScroll,
    Notification
)

from settings import (
    AUTHOR,
    CLOSE,
    DESCRIPTION,
    EMAIL,
    GREEN,
    LICENSE,
    RED,
    VAULT_TITLE,
    VERSION,
    URL,
    YELLOW
)

console = Console()


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
        self.about_vault.visible = False
        self.cells.visible = True

        self.notification.visible = False

    def action_load_data(self):
        self.load_json.visible = not self.load_json.visible
        self.dump_json.visible = False
        self.find_db.visible = False
        self.about_vault.visible = False
        self.cells.visible = not self.load_json.visible

        self.notification.visible = False

    def action_find_database(self):
        self.find_db.label = self.vlt.vault_db_ui
        self.find_db.action = lambda: self.vlt.find_database(
            verbose=False
        )

        self.find_db.visible = not self.find_db.visible
        self.dump_json.visible = False
        self.load_json.visible = False
        self.about_vault.visible = False
        self.cells.visible = True

        self.notification.visible = False

    def action_about_vault(self):
        self.about_vault.action = lambda: URL

        self.about_vault.visible = not self.about_vault.visible
        self.dump_json.visible = False
        self.load_json.visible = False
        self.find_db.visible = False
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
                loc = self.vlt.load_data(path)
                self.cells.update_cells(
                    cells=self._create_cells()
                )
                label = os.path.basename(loc)
                self.action_load_data()
                color = GREEN
            except (err.FileNotFound, err.InvalidJSON) as e:
                title = 'Error'
                label = str(e)
                color = RED
            self.notification.show(title, label, color)
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
        await self.bind('ctrl+q', 'quit', CLOSE)
        await self.bind('ctrl+d', 'dump_data', 'Dump JSON')
        await self.bind('ctrl+l', 'load_data', 'Load JSON')
        await self.bind('ctrl+f', 'find_database', 'Find DB')
        await self.bind('ctrl+a', 'about_vault', 'About')

    async def on_mount(self) -> None:
        await self.view.dock(Footer(), edge='bottom', z=2)

        self.cells = CellGrid(cells=self._create_cells())
        self.cells.visible = True

        self.notification = Notification(
            title='', label=''
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

        info = f'{VAULT_TITLE} v{VERSION} {LICENSE}'
        desc = f'{DESCRIPTION}\n{URL}'
        author = f'{AUTHOR}\n{EMAIL}'
        self.about_vault = CopyButton(
            title=f'About {self.vlt.name}',
            label=f'{info}\n\n{desc}\n\n{author}'
        )
        self.about_vault.visible = False

        await self._create_tree(os.getcwd())

        await self.view.dock(self.notification, z=2)
        await self.view.dock(self.dump_json, z=2)
        await self.view.dock(self.load_json, z=2)
        await self.view.dock(self.find_db, z=2)
        await self.view.dock(self.about_vault, z=2)
        await self.view.dock(self.cells, z=1)

        if self.vlt.is_empty():
            self.notification.show(
                'Warning',
                f'Empty {self.vlt.name}: Load JSON',
                YELLOW
            )
