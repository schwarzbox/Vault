# vault.py

import os

from rich.console import Console

from rich.console import RenderableType
from textual.app import App
from textual.widgets import ScrollView, TreeClick
from textual.reactive import Reactive

import errors as err
from widgets import (
    ActionButton,
    CellGrid,
    CellButton,
    CopyButton,
    HightlightFooter,
    InputText,
    LoadTree,
    LoadScroll,
    Notification
)
from settings import ABOUT, CLOSE, RED, URL, YELLOW

console = Console()


class ViewApp(App):
    source_type: Reactive[RenderableType] = Reactive('')

    def __init__(self, *args, vlt, **kwargs):
        super().__init__(*args, **kwargs)
        self.vlt = vlt

    def watch_source_type(self, value):
        for binding in self.bindings.shown_keys:
            if binding.key == 's':
                binding.description = value

    def _set_source_type(self):
        if self.vlt.is_local_source:
            self.source_type = 'Local Source'
            self.footer.change_style = False
        else:
            self.source_type = 'Remote Source'
            self.footer.change_style = True
        self.footer._key_text = None
        self.footer.refresh(layout=True)

    def _hide_pop_up_view(self, *exclude):
        for view in self.pop_up_views:
            if view not in exclude:
                view.visible = False

    def action_dump_data(self):
        loc = self.vlt.get_json_path()
        self.dump_json.label = os.path.basename(loc)
        self.dump_json.action = lambda: self.vlt.dump_data(
            loc, verbose=False
        )

        self.dump_json.visible = not self.dump_json.visible
        self._hide_pop_up_view(self.dump_json)
        self.cells.visible = True

    def action_load_data(self):
        self.load_json.visible = not self.load_json.visible
        self._hide_pop_up_view(self.load_json)
        self.cells.visible = not self.load_json.visible

    def _erase_data(self):
        try:
            self.vlt.erase_data()
            self.cells.update_cells(cells=self._create_cells())
            self._show_warning_load_json()
        except (
            err.ActionNotAllowedForRemote,
            err.LocalDataBaseNotFound
        ) as e:
            title = 'Error'
            label = str(e)
            color = RED
            self.notification.show(title, label, color)

    def action_erase_data(self):
        login, password = (
            self.vlt.encoder.decode(self.vlt.key).split(' ')
        )
        label = f"{login} {'*' * len(password)}"
        self.erase_data.label = label
        self.erase_data.action = self._erase_data

        self.erase_data.visible = not self.erase_data.visible
        self._hide_pop_up_view(self.erase_data)
        self.cells.visible = True

    def action_find_database(self):
        loc = self.vlt.get_database_path()
        self.find_db.label = loc
        self.find_db.action = lambda: self.vlt.find_database(
            loc, verbose=False
        )

        self.find_db.visible = not self.find_db.visible
        self._hide_pop_up_view(self.find_db)
        self.cells.visible = True

    def _source_data(self):
        login, password = (
            self.vlt.encoder.decode(self.vlt.key).split(' ')
        )
        old_key = self.vlt.key
        old_source = self.vlt.vault_db
        source = self.input_source.content
        try:
            self.input_source.content = ''
            self.input_source.hide()

            self.vlt.set_source(source)
            self.vlt.get_user(login, password)
            self.cells.update_cells(cells=self._create_cells())
            self._show_warning_load_json()
        except (
            err.LocalDataBaseNotFound,
            err.FileNotFound,
            err.InvalidJSON,
            err.InvalidDataFormat,
            err.InvalidURL,
            err.LoginFailed
        ) as e:
            title = 'Error'
            label = str(e)
            color = RED

            self.notification.show(title, label, color)

            try:
                self.vlt.key = old_key
                self.vlt.set_source(old_source)
                self.vlt.get_user(login, password)
                self.set_timer(
                    2, self._show_warning_load_json
                )
            except err.LoginFailed:
                self.vlt.key = old_key
                self.vlt.set_source(old_source)
                self.vlt.set_user(login, password)
                self.set_timer(
                    2, self._show_warning_load_json
                )
            except (
                err.LocalDataBaseNotFound,
                err.FileNotFound,
                err.InvalidJSON,
                err.InvalidDataFormat,
                err.InvalidURL,
                err.LoginFailed
            ) as e:
                label = str(e)

                self.set_timer(
                    2,
                    lambda: self.notification.show(
                        title, label, color
                    )
                )
        self._set_source_type()

    def action_source_data(self):
        self.input_button.action = self._source_data

        self.input_source.visible = not self.input_source.visible
        self.input_button.visible = not self.input_button.visible
        self._hide_pop_up_view(self.input_button, self.input_source)
        self.cells.visible = True

    def action_about_vault(self):
        self.about_vault.action = lambda: URL

        self.about_vault.visible = not self.about_vault.visible
        self._hide_pop_up_view(self.about_vault)
        self.cells.visible = True

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
                self._show_warning_load_json()
            except (
                err.ActionNotAllowedForRemote,
                err.LocalDataBaseNotFound,
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

    def _show_warning_load_json(self):
        if self.vlt.is_empty:
            self.notification.show(
                'Warning', 'Empty: Load JSON', YELLOW, 3
            )

    async def on_load(self) -> None:

        await self.bind('ctrl+c', 'quit', CLOSE)
        await self.bind('d', 'dump_data', 'Dump')
        await self.bind('l', 'load_data', 'Load')
        await self.bind('e', 'erase_data', 'Erase')
        await self.bind('f', 'find_database', 'Find')
        await self.bind('s', 'source_data', 'Source')
        await self.bind('a', 'about_vault', ABOUT)

    async def on_mount(self) -> None:

        self.footer = HightlightFooter()
        await self.view.dock(self.footer, edge='bottom', z=2)

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

        self.input_source = InputText(title='Source')
        self.input_button = ActionButton(
            title='', label='Connect'
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
            self.input_source, self.input_button, z=2
        )
        await self.view.dock(self.cells, z=1)

        self._show_warning_load_json()
        self._set_source_type()

        self.pop_up_views = [
            self.dump_json,
            self.input_source,
            self.input_button,
            self.load_json,
            self.erase_data,
            self.find_db,
            self.about_vault,
            self.notification,
        ]
