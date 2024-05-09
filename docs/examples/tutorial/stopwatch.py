from time import monotonic
from enum import Enum
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Static, Input

class StopwatchMode(Enum):
    COUNTDOWN = "COUNTDOWN" # Timer
    COUNTUP = "COUNTUP" # Stopwatch

# Stopwatch display
class TimeDisplay(Input):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        """Method to update time to current."""
        self.time = self.total + (monotonic() - self.start_time)

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.value = f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}"

    def start(self, mode: StopwatchMode = StopwatchMode.COUNTUP) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self):
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def reset(self):
        """Method to reset the time display to zero."""
        self.total = 0
        self.time = 0

class TimerDisplay(Input):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = reactive(0.0)

    def __init__(self, time: float = 90.0):
        super().__init__()
        self.time = time

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        """Method to update time to current."""
        self.time = self.total - (monotonic() - self.start_time)
        if self.time < 0:
            self.stop()

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.value = f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}"

    def start(self, mode: StopwatchMode = StopwatchMode.COUNTUP) -> None:
        """Method to start (or resume) time updating."""
        colons = reversed(self.value.split(":"))
        self.total = sum(float(x) * (60 ** i) for i, x in enumerate(colons))
        # datetime.strptime("0:09:1", '%H:%M:%S')

        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self):
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.time = self.total

    def reset(self):
        """Method to reset the time display to zero."""
        self.time = self.total

class Stopwatch(Static):
    """A stopwatch widget."""
    _stopwatch_mode = StopwatchMode.COUNTUP

    def __init__(self, stopwatch_mode: StopwatchMode = StopwatchMode.COUNTUP):
        super().__init__()
        self._stopwatch_mode = stopwatch_mode

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id

        time_display = None
        try:
            time_display = self.query_one(TimeDisplay)
        except:
            pass
        if not time_display:
            try:
                time_display = self.query_one(TimerDisplay)
            except:
                pass

        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()

    # The weird thing about this is you add another button, then TimeDisplay doesn't automatically layout
    # its size using the remaining space. It'll overlap with the reset button.
    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        if self._stopwatch_mode == StopwatchMode.COUNTUP:
            yield Button("Start", id="start", variant="success")
        else:
            yield Button("Countdown", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        if self._stopwatch_mode == StopwatchMode.COUNTUP:
            yield TimeDisplay()
        else:
            yield TimerDisplay()


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "stopwatch.tcss"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("a", "add_stopwatch", "Add stopwatch"),
        ("t", "add_timer", "Add timer"),
        ("r", "remove_stopwatch", "Remove"),
        ("m", "toggle_stopwatch_mode", "Toggle mode")
    ]

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield Footer()
        yield ScrollableContainer(Stopwatch(), Stopwatch(StopwatchMode.COUNTDOWN), Stopwatch(), id="timers")

    def action_add_stopwatch(self) -> None:
        """An action to add a stopwatch."""
        new_stopwatch = Stopwatch()
        self.query_one("#timers").mount(new_stopwatch)
        new_stopwatch.scroll_visible()

    def action_add_timer(self) -> None:
        """An action to add a timer."""
        new_stopwatch = Stopwatch(StopwatchMode.COUNTDOWN)
        self.query_one("#timers").mount(new_stopwatch)
        new_stopwatch.scroll_visible()

    def action_remove_stopwatch(self) -> None:
        """Called to remove a timer."""
        timers = self.query("Stopwatch")
        if timers:
            timers.last().remove()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
