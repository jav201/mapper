"""Spike: does Textual dispatch action_*, on_* and BINDINGS through plain (non-widget) mixins?"""
import asyncio
import textual
from textual.app import App
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Static

log = []


class KeysMixin:
    BINDINGS = [Binding("x", "from_mixin", "mixin action")]

    def action_from_mixin(self):
        log.append("action_from_mixin")

    def on_mount(self):
        log.append("on_mount(mixin)")


class ResizeMixin:
    def on_mount(self):
        log.append("on_mount(mixin2)")

    def on_resize(self, event):
        log.append("on_resize(mixin)")


class Core(KeysMixin, ResizeMixin, Screen):
    BINDINGS = [Binding("y", "from_core", "core action"), Binding("z", "from_mixin", "core binding to mixin action")]

    def compose(self):
        yield Static("hi")

    def action_from_core(self):
        log.append("action_from_core")


class A(App):
    def on_mount(self):
        self.push_screen(Core())


async def main():
    app = A()
    async with app.run_test(size=(40, 10)) as pilot:
        await pilot.pause()
        await pilot.press("x")
        await pilot.press("y")
        await pilot.press("z")
        await pilot.pause()
        keys = sorted(app.screen._bindings.key_to_bindings)
        print("textual", textual.__version__)
        print("log", log)
        print("screen bindings", keys)


asyncio.run(main())
