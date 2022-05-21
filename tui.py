# vault.py

import os

from rich.console import Console

from textual.app import App
from textual.widgets import Footer, ScrollView, TreeClick

import errors as err
from widgets import (
    ActionButton,
    CellGrid,
    CellButton,
    CopyButton,
    InputText,
    LoadTree,
    LoadScroll,
    Notification
)
from settings import ABOUT, CLOSE, LOCAL, RED, URL, YELLOW

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
        self.input_remote.visible = False
        self.input_button.visible = False
        self.load_json.visible = False
        self.erase_data.visible = False
        self.find_db.visible = False
        self.about_vault.visible = False
        self.cells.visible = True
        self.notification.visible = False

    def action_load_data(self):
        self.load_json.visible = not self.load_json.visible
        self.input_remote.visible = False
        self.input_button.visible = False
        self.dump_json.visible = False
        self.erase_data.visible = False
        self.find_db.visible = False
        self.about_vault.visible = False
        self.cells.visible = not self.load_json.visible
        self.notification.visible = False

    def _erase_data(self):
        try:
            self.vlt.erase_data()
            self.cells.update_cells(cells=self._create_cells())
        except (
            err.ActionNotAllowedForRemote,
            err.DataBaseNotFound
        ) as e:
            title = 'Error'
            label = str(e)
            color = RED
            self.notification.show(title, label, color)

    def action_erase_data(self):
        self.erase_data.label = self.vlt.encoder.decode(self.vlt.key)
        self.erase_data.action = self._erase_data

        self.erase_data.visible = not self.erase_data.visible
        self.input_remote.visible = False
        self.input_button.visible = False
        self.dump_json.visible = False
        self.load_json.visible = False
        self.find_db.visible = False
        self.about_vault.visible = False
        self.cells.visible = True
        self.notification.visible = False

    def action_find_database(self):
        loc = self.vlt.get_database_path()
        self.find_db.label = loc
        self.find_db.action = lambda: self.vlt.find_database(
            loc, verbose=False
        )

        self.find_db.visible = not self.find_db.visible
        self.input_remote.visible = False
        self.input_button.visible = False
        self.dump_json.visible = False
        self.load_json.visible = False
        self.erase_data.visible = False
        self.about_vault.visible = False
        self.cells.visible = True
        self.notification.visible = False

    def _source_data(self):
        login, password = (
            self.vlt.encoder.decode(self.vlt.key).split(' ')
        )
        source = self.input_remote.content

        try:
            self.input_remote.content = ''
            self.input_remote.hide()

            self.vlt.source = source
            self.vlt.set_remote_source()
            self.vlt.get_user(login, password)

        except (
            err.DataBaseNotFound,
            err.FileNotFound,
            err.InvalidJSON,
            err.InvalidDataFormat,
            err.InvalidURL,
            err.LoginFailed
        ) as e:
            self.vlt.source = LOCAL
            self.vlt.set_local_source()
            self.vlt.get_user(login, password)

            title = 'Error'
            label = str(e)
            color = RED
            self.notification.show(title, label, color)

        self.cells.update_cells(cells=self._create_cells())

    def action_source_data(self):
        self.input_remote.visible = not self.input_remote.visible
        self.input_button.visible = not self.input_button.visible
        self.input_button.action = self._source_data

        self.dump_json.visible = False
        self.load_json.visible = False
        self.erase_data.visible = False
        self.find_db.visible = False
        self.about_vault.visible = False
        self.cells.visible = True
        self.notification.visible = False

    def action_about_vault(self):
        self.about_vault.action = lambda: URL

        self.about_vault.visible = not self.about_vault.visible
        self.input_remote.visible = False
        self.input_button.visible = False
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
            try:
                self.action_load_data()
                self.vlt.load_data(path)
                self.cells.update_cells(cells=self._create_cells())
            except (
                err.ActionNotAllowedForRemote,
                err.DataBaseNotFound,
                err.FileNotFound,
                err.InvalidJSON,
                err.InvalidDataFormat
            ) as e:
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
        await self.bind('ctrl+c', 'quit', CLOSE)
        await self.bind('d', 'dump_data', 'Dump')
        await self.bind('l', 'load_data', 'Load')
        await self.bind('e', 'erase_data', 'Erase')
        await self.bind('f', 'find_database', 'Find')
        await self.bind('s', 'source_data', 'Source')
        await self.bind('a', 'about_vault', ABOUT)

    async def on_mount(self) -> None:
        await self.view.dock(Footer(), edge='bottom', z=2)

        self.cells = CellGrid(cells=self._create_cells())
        self.cells.visible = True

        self.notification = Notification(
            title='', label=''
        )

        self.dump_json = CopyButton(
            title='Dump', label=''
        )

        self.load_json = ScrollView()
        self.load_json.vscroll = LoadScroll(vertical=True)
        self.load_json.hscroll = LoadScroll(vertical=False)
        self.load_json.visible = False

        self.erase_data = ActionButton(title='Erase', label='')

        self.find_db = CopyButton(title='Find', label='')

        self.input_remote = InputText(title='Source')
        self.input_button = ActionButton(
            title='', label='Remote'
        )

        self.about_vault = CopyButton(
            title='About',
            label=self.vlt.about(verbose=False)
        )

        await self._create_tree(os.getcwd())

        await self.view.dock(self.notification, z=2)
        await self.view.dock(self.dump_json, z=2)
        await self.view.dock(self.load_json, z=2)
        await self.view.dock(self.erase_data, z=2)
        await self.view.dock(self.find_db, z=2)
        await self.view.dock(self.about_vault, z=2)
        await self.view.dock(
            self.input_remote, self.input_button, z=2
        )
        await self.view.dock(self.cells, z=1)

        if self.vlt.is_empty:
            self.notification.show(
                'Warning',
                'Empty: Load JSON',
                YELLOW,
                3
            )
