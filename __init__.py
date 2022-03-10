from typing import *

from anki.cards import Card
from aqt import gui_hooks
from aqt import mw, operations
from aqt import qconnect
from aqt.qt import QAction, QMessageBox
from aqt.utils import showInfo, tooltip
from itertools import pairwise

from .qwerty import *

import subprocess as sp


def error_times_to_ease(error_times: int, thresholds: List[int]) -> Literal[1, 2, 3, 4]:
    ease: Literal[1, 2, 3, 4]
    for threshold, ease in zip(thresholds, [1, 2, 3]):
        if error_times >= threshold:
            return ease
    return 4


class Config:
    thresholds: List[int]
    command: Optional[str]

    def __init__(self, thresholds: List[int], command: str):
        if self.are_thresholds_valid(thresholds):
            self.thresholds = thresholds
        else:
            raise ValueError
        self.command = command

    @staticmethod
    def are_thresholds_valid(thresholds: List[int]) -> bool:
        return len(thresholds) == 3 \
               and all([a >= b for (a, b) in pairwise(thresholds)])


class State:
    config: Config
    con: Optional[Connection]
    is_enabled: bool
    action: QAction

    def __init__(self, config: Config):
        self.is_enabled = False
        self.config = config
        self.action = QAction("Enable qwerty", mw)
        self.con = None

    def add_to_menu(self):
        qconnect(self.action.triggered, lambda: State.toggle_enable(self))
        mw.form.menuTools.addSeparator()
        mw.form.menuTools.addAction(self.action)

    def disable(self):
        self.is_enabled = False
        self.action.setText("Enable qwerty")
        self.con.close()
        self.con = None
        gui_hooks.reviewer_did_show_question.remove(self.prompt_a_word)

    def toggle_enable(self):
        if not self.is_enabled:
            try:
                if self.con is None:
                    self.con = Connection()
                self.is_enabled = True
                self.action.setText("Enable qwerty ✓")
                gui_hooks.reviewer_did_show_question.append(self.prompt_a_word)
                gui_hooks.profile_will_close.append(self.con.close)
            except (ConnectionRefusedError, FileNotFoundError):
                open_button = QMessageBox.StandardButton(QMessageBox.Open)
                cancel_button = QMessageBox.StandardButton(QMessageBox.Cancel)
                result = showInfo(
                    "Cannot connect to qwerty. Open qwerty?",
                    title="qwerty addon",
                    customBtns=[open_button, cancel_button]
                )
                if result == QMessageBox.Open:
                    self.open_qwerty()
        else:
            self.disable()

    def open_qwerty(self):
        command = self.config.command
        if command:
            def toggle_after_some_time():
                time.sleep(0.5)
                self.toggle_enable()

            try:
                sp.Popen(command.split())
                op = operations.QueryOp(
                    op=lambda _: toggle_after_some_time(),
                    parent=mw.app.activeWindow(),
                    success=lambda _: tooltip("Connected.")
                )
                op.with_progress("Connecting...")
                op.run_in_background()
            except OSError:
                showInfo("Failed to execute:\n"
                         f"{command}\n"
                         "Check your configuration.")

    def communicate(self, word: str, _c: Collection):
        self.con.send_word(word)
        return self.con.receive_error_times()

    def prompt_a_word(self, card: Card):
        items = card.note().items()
        for (k, v) in items:
            if k == "Back":
                word = v
                op = operations.QueryOp(op=lambda col: self.communicate(word, col),
                                        success=self.answer_the_card,
                                        parent=mw.app.activeWindow())
                op.failure(self.on_failure)
                op.run_in_background()
                break

    def on_failure(self, err):
        msg = ""
        if isinstance(err, OSError):
            msg = "Failed to connect to qwerty.\n" \
                  "Maybe qwerty isn't running anymore."
        if isinstance(err, ValueError):
            msg = "Qwerty quits."
        if self.is_enabled:
            self.disable()
            showInfo(
                msg
                + "\nQwerty addon disabled."
                  "\nReturning to deck browser.",
                title="qwerty addon",
            )
            mw.deckBrowser.show()

    def answer_the_card(self, error_times):
        mw.reviewer._showAnswer()
        ease = error_times_to_ease(error_times, self.config.thresholds)
        tooltip(f"Misspell times: {str(error_times)}\n"
                f"Ease: {ease}")
        mw.reviewer._answerCard(ease)
        pass


def main():
    config = Config(**mw.addonManager.getConfig(__name__))
    state = State(config)
    state.add_to_menu()


main()
