# vault.py

import os
from typing import TypeVar

import pyperclip as pc

from rich.align import Align
from rich.box import HEAVY
from rich.color import Color
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

from textual import events
from textual.scrollbar import ScrollBar, ScrollBarRender
from textual.views import GridView
from textual.widget import Widget
from textual.widgets import (
    Button, Footer, TreeControl, TreeNode
)

from mixins import ButtonMixin, InputTextMixin
from settings import (
    ACTION_TIME,
    BRIGHT_GREEN,
    COPY,
    DONE,
    GRAY,
    GREEN,
    KEY,
    LOCAL_STYLE,
    NOTIFICATION_TIME,
    YELLOW
)

NodeDataType = TypeVar('NodeDataType')


class CellGrid(GridView):
    def __init__(self, *args, cells, **kwargs):
        super().__init__(*args, **kwargs)
        self.cells = cells

    async def on_mount(self) -> None:
        self.grid.add_column(
            'col',
            fraction=1,
            min_size=8,
            max_size=24,
            repeat=4
        )
        self.grid.add_row(
            'row',
            fraction=1,
            max_size=3
        )
        self.grid.set_repeat(True, True)
        self.grid.set_align('center', 'center')
        self.update_cells(self.cells)

    def update_cells(self, cells, repeat_grid=(True, True)) -> None:
        self.grid.set_repeat(*repeat_grid)
        self.grid.widgets.clear()
        self.grid.place(*cells)
        self.refresh()


class CellButton(ButtonMixin, Button):
    def __init__(
        self, *args, encoder, title, value, action, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.encoder = encoder
        self.title = self.encoder.decode(title)
        self.label = self.encoder.decode(self.label)
        self.value = value
        self.on_click_label = KEY

        self.action = (
            action
            or (lambda title, label, value: pc.copy(value))
        )

    def on_click(self) -> None:
        super().on_click()
        self.action(
            self.title, self.label, self.encoder.decode(self.value)
        )


class CopyButton(ButtonMixin, Button):
    def __init__(
        self, *args, title, sec=ACTION_TIME, action=None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.title = title
        self.on_click_label = COPY
        self.action = action
        self.visible = False
        self.sec = sec

    def hide(self):
        self.visible = False

    def on_click(self) -> None:
        super().on_click()
        if self.action:
            loc = self.action()
            if loc:
                pc.copy(loc)
        if self.sec:
            self.set_timer(self.sec, lambda: self.hide())
        else:
            self.hide()


class ActionButton(ButtonMixin, Button):
    def __init__(
        self, *args, title, sec=ACTION_TIME, action=None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.title = title
        self.on_click_label = DONE
        self.action = action
        self.visible = False
        self.sec = sec

    def hide(self):
        self.visible = False

    def _hide_action(self):
        self.hide()
        if self.action:
            self.action()

    def on_click(self) -> None:
        super().on_click()
        if self.sec:
            self.set_timer(self.sec, lambda: self._hide_action())
        else:
            self._hide_action()


class Notification(Widget):
    def __init__(self, title: str, label: str):
        super().__init__(title)
        self.title = title
        self.label = label
        self.border_color = GREEN
        self.visible = False

    def render(self) -> Panel:
        return Panel(
            Align.center(
                Text(self.label),
                vertical='middle',
                style=GREEN
            ),
            title=self.title,
            title_align='left',
            border_style=Style(color=self.border_color),
            box=HEAVY
        )

    def on_click(self) -> None:
        self.visible = False

    def hide(self):
        self.visible = False

    def show(self, title, label, color=GREEN, sec=NOTIFICATION_TIME):
        self.title = title
        self.label = label
        self.border_color = color
        self.visible = True

        if sec:
            self.set_timer(sec, lambda: self.hide())


class LoadScroll(ScrollBar):
    def render(self) -> RenderableType:
        style = Style(
            bgcolor=Color.parse(GRAY),
            color=GREEN,
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
                    self.root.id, folder, {'dir': folder}
                )
            else:
                await self.add(
                    self.root.id, folder, {'path': folder}
                )

        self.refresh(layout=True)

    def render_node(
        self, node: TreeNode[NodeDataType]
    ) -> RenderableType:

        color = GRAY
        is_clickable = False
        if os.path.isdir(node.label):
            try:
                os.listdir(node.label)
                color = BRIGHT_GREEN
                is_clickable = True
            except PermissionError:
                pass
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


class InputText(InputTextMixin):
    def __init__(self, title: str, content: str):
        super().__init__()
        self.title = title
        self.content = content
        self.visible = False

    def on_key(self, event: events.Key) -> None:
        if self.mouse_over:
            if str(event.key) == 'ctrl+v':
                self.content = ''
                self.content += pc.paste()
                self.refresh()

    def hide(self):
        self.visible = False


class HighlightFooter(Footer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style = LOCAL_STYLE

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, style):
        self._style = style

    def make_key_text(self) -> Text:
        text = Text(
            style=self.style,
            no_wrap=True,
            overflow='ellipsis',
            justify='left',
            end='',
        )
        for binding in self.app.bindings.shown_keys:
            key_display = (
                binding.key.upper()
                if binding.key_display is None
                else binding.key_display
            )
            hovered = self.highlight_key == binding.key
            key_text = Text.assemble(
                (f' {key_display} ', 'reverse' if hovered else 'default on default'),
                f' {binding.description} ',
                meta={'@click': f"app.press('{binding.key}')", 'key': binding.key},
            )
            text.append_text(key_text)
        return text
