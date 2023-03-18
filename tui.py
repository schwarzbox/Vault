# vault.py

import os
from enum import Enum

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
    HighlightFooter,
    InputText,
    LoadTree,
    LoadScroll,
    Notification
)
from settings import (
    ADD,
    ADD_LABEL,
    CANCEL_LABEL,
    CLEAR,
    CLOSE,
    DEFAULT_LABEL,
    DUMP,
    EDIT,
    FAST_ACTION_TIME,
    FIND,
    GREEN,
    EMPTY_JSON_TIME,
    ERROR_LABEL,
    INFO,
    LOAD,
    LOCAL,
    LOCAL_STYLE,
    NOTIFICATION_LABEL,
    NOTIFICATION_TIME,
    OK_LABEL,
    PASTE_LABEL,
    RED,
    REMOTE,
    REMOTE_STYLE,
    UPDATE,
    UPDATE_STYLE,
    SOURCE,
    URL,
    UPDATE_LABEL,
    WARNING_LABEL,
    WHO,
    YELLOW
)


console = Console()


class State(Enum):
    LOCAL = 1
    REMOTE = 2
    UPDATE = 3


class ViewApp(App):
    state_type: Reactive[RenderableType] = Reactive('')

    def __init__(self, *args, vlt, **kwargs):
        super().__init__(*args, **kwargs)
        self.vlt = vlt
        self.state = State.LOCAL

    def watch_state_type(self, value):
        for binding in self.bindings.shown_keys:
            if binding.key == 's':
                binding.description = value

    def _set_source_mode(self):
        if self.state == State.UPDATE:
            self.cells_grid.update_cells(
                cells=self._create_cells()
            )

        if self.vlt.is_local_source:
            self.state = State.LOCAL
            self.state_type = f'{SOURCE} {LOCAL}'
            self.footer.style = LOCAL_STYLE
        else:
            self.state = State.REMOTE
            self.state_type = f'{SOURCE} {REMOTE}'
            self.footer.style = REMOTE_STYLE

        self.footer._key_text = None
        self.footer.refresh(layout=True)

    def _set_edit_mode(self):
        if self.state == State.LOCAL:
            self.state = State.UPDATE
            self.state_type = f'{SOURCE} {UPDATE}'
            self.footer.style = UPDATE_STYLE

            self._process_edit_cells()

        elif self.state == State.UPDATE:
            self.state = State.LOCAL
            self.state_type = f'{SOURCE} {LOCAL}'
            self.footer.style = LOCAL_STYLE

            self.cells_grid.update_cells(
                cells=self._create_cells()
            )

        self.footer._key_text = None
        self.footer.refresh(layout=True)

    def _is_remote_state(self):
        if self.state == State.REMOTE:
            raise err.ActionNotAllowedForRemote

    def _show_notification_load_json(self):
        if self.vlt.is_empty:
            self.notification.show(
                WARNING_LABEL,
                'Empty: Load JSON',
                YELLOW,
                EMPTY_JSON_TIME
            )

    def _hide_pop_up_view(self, *exclude):
        for view in self.pop_up_views:
            if view not in exclude:
                view.visible = False

    # actions

    def action_whoami(self):
        self.whoami.action = (
            lambda: self.notification.show(
                NOTIFICATION_LABEL,
                self.vlt.encoder.decode(self.vlt.key),
                GREEN
            )
        )

        self.whoami.visible = not self.whoami.visible

        self._hide_pop_up_view(self.whoami)
        self.cells_grid.visible = True
        self._set_source_mode()

    def _dump_data(self, loc):
        try:
            return self.vlt.dump_data(loc, verbose=False)
        except err.ActionNotAllowedForRemote as e:
            self.notification.show(ERROR_LABEL, str(e), RED)

    def action_dump_data(self):
        try:
            self._is_remote_state()
        except err.ActionNotAllowedForRemote as e:
            self.notification.show(ERROR_LABEL, str(e), RED)
            return

        loc = self.vlt.get_json_path()
        self.dump_json.label = os.path.basename(loc)
        self.dump_json.action = lambda: self._dump_data(loc)

        self.dump_json.visible = not self.dump_json.visible

        self._hide_pop_up_view(self.dump_json)
        self.cells_grid.visible = True
        self._set_source_mode()

    def action_load_data(self):
        try:
            self._is_remote_state()
        except err.ActionNotAllowedForRemote as e:
            self.notification.show(ERROR_LABEL, str(e), RED)
            return

        self.load_json.visible = not self.load_json.visible

        self._hide_pop_up_view(self.load_json)
        self.cells_grid.visible = not self.load_json.visible
        self._set_source_mode()

    def _process_edit_view(self, group='', key='', value=''):
        self.edit_cancel.visible = not self.edit_cancel.visible
        self.edit_group.visible = not self.edit_group.visible
        self.edit_key.visible = not self.edit_key.visible
        self.edit_value.visible = not self.edit_value.visible
        self.edit_button.visible = not self.edit_button.visible

        self.edit_group.label = group
        self.edit_key.label = key
        self.edit_value.label = value

    def _process_edit_data(self, edit_action):
        self.edit_cancel.hide()
        self.edit_group.hide()
        self.edit_key.hide()
        self.edit_value.hide()

        try:
            edit_action()
            self._process_edit_cells()
        except (
            err.GroupAlreadyExists,
            err.GroupNotExists,
            err.KeyAlreadyExists,
            err.KeyNotExists,
            err.ActionNotAllowedForRemote,
            err.LocalDataBaseNotFound
        ) as e:
            self.notification.show(ERROR_LABEL, str(e), RED)

    def action_context(self, action, **kwargs):
        return lambda: self._process_edit_data(
            lambda: action(**kwargs)
        )

    def _add_data(self):
        self.vlt.add_data(
            self.edit_group.label,
            self.edit_key.label,
            self.edit_value.label
        )

    def _update_data(self, group, key):
        self.vlt.update_data(
            group,
            self.edit_group.label,
            key,
            self.edit_key.label,
            self.edit_value.label
        )

    def _clear_data(self, group, key):
        self.vlt.clear_data(group, key)
        self._show_notification_load_json()

    def _add_view(self, group='', key='', value=''):
        self._process_edit_view('Group', 'Key', 'Value')
        self.edit_cancel.title = ADD_LABEL
        self.edit_button.action = self.action_context(
            self._add_data
        )

    def _update_view(self, group='', key='', value=''):
        self._process_edit_view(group, key, value)
        self.edit_cancel.title = UPDATE_LABEL
        self.edit_button.action = self.action_context(
            self._update_data,
            group=group,
            key=key
        )

    def _process_edit_cells(self):
        cells = self._create_cells(self._update_view)
        final_cells = []
        for cell in cells:
            final_cells.append(cell)

            clear_cell = ActionButton(
                title='',
                label=CLEAR,
                sec=FAST_ACTION_TIME,
                action=self.action_context(
                    self._clear_data,
                    group=cell.title,
                    key=cell.label
                )
            )
            final_cells.append(clear_cell)
        final_cells.append(
            ActionButton(
                title='',
                label=ADD,
                sec=FAST_ACTION_TIME,
                action=self._add_view
            )
        )

        self.cells_grid.update_cells(
            # set repeat this way to allow edit all cells
            cells=final_cells, repeat_grid=(True, True)
        )

    def action_edit_data(self):
        try:
            self._is_remote_state()
        except err.ActionNotAllowedForRemote as e:
            self.notification.show(ERROR_LABEL, str(e), RED)
            return

        self._hide_pop_up_view()
        self._set_edit_mode()

        self.cells_grid.visible = True

    def _set_source(self):
        login, password = (
            self.vlt.encoder.decode(self.vlt.key).split(' ')
        )
        old_key = self.vlt.key
        old_source = self.vlt.vault_db
        source = self.source_update.label

        self.source_update.label = self.vlt.get_default_source()
        self.source_update.hide()
        try:
            self.vlt.set_source(source)
            self.vlt.get_user(login, password)
            self.cells_grid.update_cells(cells=self._create_cells())
            self._show_notification_load_json()
        except (
            err.LocalDataBaseNotFound,
            err.FileNotFound,
            err.InvalidJSON,
            err.InvalidDataFormat,
            err.InvalidURL,
            err.LoginFailed
        ) as e:
            title = ERROR_LABEL
            label = str(e)
            color = RED

            self.notification.show(title, label, color)

            try:
                self.vlt.key = old_key
                self.vlt.set_source(old_source)
                self.vlt.get_user(login, password)
                self.set_timer(
                    NOTIFICATION_TIME,
                    self._show_notification_load_json
                )
            except err.LoginFailed:
                self.vlt.key = old_key
                self.vlt.set_source(old_source)
                self.vlt.set_user(login, password)
                self.set_timer(
                    NOTIFICATION_TIME,
                    self._show_notification_load_json
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
                    NOTIFICATION_TIME,
                    lambda: self.notification.show(
                        title, label, color
                    )
                )

        self._set_source_mode()

    def action_set_source(self):
        self.source_update.label = self.vlt.get_default_source()
        self.source_update.visible = not self.source_update.visible
        self.source_button.visible = not self.source_button.visible

        self._hide_pop_up_view(
            self.source_update,
            self.source_button
        )
        self.cells_grid.visible = True

        self._set_source_mode()

    def _find_database(self, loc):
        try:
            return self.vlt.find_database(loc, verbose=False)
        except err.LocalDataBaseNotFound as e:
            self.notification.show(ERROR_LABEL, str(e), RED)

    def action_find_database(self):
        loc = self.vlt.get_database_path()
        self.find_db.label = loc
        self.find_db.action = lambda: self._find_database(loc)

        self.find_db.visible = not self.find_db.visible

        self._hide_pop_up_view(self.find_db)
        self.cells_grid.visible = True
        self._set_source_mode()

    def action_info_vault(self):
        self.info_vault.visible = not self.info_vault.visible

        self._hide_pop_up_view(self.info_vault)
        self.cells_grid.visible = True
        self._set_source_mode()

    async def handle_tree_click(
        self, message: TreeClick[dict]
    ) -> None:

        path = message.node.data.get('path', None)
        directory = message.node.data.get('dir', None)

        if path:
            try:
                self.action_load_data()
                self.vlt.load_data(path)
                self.cells_grid.update_cells(
                    cells=self._create_cells()
                )
                self._show_notification_load_json()
            except (
                err.ActionNotAllowedForRemote,
                err.LocalDataBaseNotFound,
                err.FileNotFound,
                err.InvalidJSON,
                err.InvalidDataFormat
            ) as e:
                self.notification.show(ERROR_LABEL, str(e), RED)
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

    def _create_cells(self, action=None):
        instances = []
        for group in self.vlt.vault:
            for key in self.vlt.vault[group]:
                value = self.vlt.vault.get(group, {})
                instances.append(
                    CellButton(
                        encoder=self.vlt.encoder,
                        title=group,
                        label=key,
                        value=value.get(key),
                        action=action,
                        name='cell',
                    )
                )
        return instances

    async def on_load(self) -> None:
        await self.bind('ctrl+c', '', CLOSE, show=False)
        await self.bind('ctrl+q', 'quit', CLOSE)
        await self.bind('w', 'whoami', WHO)
        await self.bind('d', 'dump_data', DUMP)
        await self.bind('l', 'load_data', LOAD)
        await self.bind('e', 'edit_data', EDIT)
        await self.bind('s', 'set_source', SOURCE)
        await self.bind('f', 'find_database', FIND)
        await self.bind('i', 'info_vault', INFO)

    async def on_mount(self) -> None:

        self.footer = HighlightFooter()
        await self.view.dock(self.footer, edge='bottom', z=2)

        self.cells_grid = CellGrid(cells=self._create_cells())
        self.cells_grid.visible = True

        self.notification = Notification(
            title='', label=''
        )

        self.whoami = ActionButton(
            title=WHO, label=OK_LABEL
        )

        self.dump_json = CopyButton(
            title=DUMP, label=''
        )

        self.load_json = ScrollView()
        self.load_json.vscroll = LoadScroll(vertical=True)
        self.load_json.hscroll = LoadScroll(vertical=False)
        self.load_json.visible = False

        self.source_update = InputText(
            title=PASTE_LABEL, label=self.vlt.get_default_source(),
        )
        self.source_button = ActionButton(
            title=SOURCE,
            label=OK_LABEL,
            action=self._set_source
        )

        self.edit_cancel = ActionButton(
            title=UPDATE_LABEL,
            label=CANCEL_LABEL,
            action=self._hide_pop_up_view,
            sec=FAST_ACTION_TIME
        )

        self.edit_group = InputText(
            title=PASTE_LABEL, label=''
        )
        self.edit_key = InputText(
            title=PASTE_LABEL, label=''
        )
        self.edit_value = InputText(
            title=PASTE_LABEL, label=''
        )
        self.edit_button = ActionButton(
            title=EDIT, label=OK_LABEL
        )

        self.find_db = CopyButton(title=FIND, label='')

        self.info_vault = CopyButton(
            title=INFO,
            label=self.vlt.info(verbose=False),
            action=lambda: URL
        )

        await self._create_tree(os.getcwd())

        await self.view.dock(self.notification, z=2)
        await self.view.dock(self.whoami, z=2)
        await self.view.dock(self.dump_json, z=2)
        await self.view.dock(self.load_json, z=2)
        await self.view.dock(
            self.source_update,
            self.source_button,
            z=2
        )
        await self.view.dock(
            self.edit_cancel,
            self.edit_group,
            self.edit_key,
            self.edit_value,
            self.edit_button,
            z=2
        )
        await self.view.dock(self.find_db, z=2)
        await self.view.dock(self.info_vault, z=2)

        await self.view.dock(self.cells_grid, z=1)

        self._show_notification_load_json()
        self._set_source_mode()

        self.pop_up_views = [
            self.whoami,
            self.dump_json,
            self.load_json,
            self.source_update,
            self.source_button,
            self.edit_cancel,
            self.edit_group,
            self.edit_key,
            self.edit_value,
            self.edit_button,
            self.find_db,
            self.info_vault,
            self.notification,
        ]
