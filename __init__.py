from typing import *

from aqt import gui_hooks
from anki.cards import Card
from aqt import mw, operations, reviewer
from aqt import qconnect
from aqt.qt import QAction
from aqt.utils import showInfo, showText, tooltip

from .qwerty import *


def error_times_to_ease(error_times: int) -> Literal[1, 2, 3, 4]:
    if error_times == 0:
        return 4
    if error_times <= 1:
        return 2
    return 1


class State:
    con: Optional[Connection]
    is_enabled: bool

    def __init__(self, is_enabled: bool):
        self.is_enabled = is_enabled
        self.con = None

    def prompt_a_word(self, card: Card):
        items = card.note().items()
        for (k, v) in items:
            if k == "Back":
                word = v
                self.con.send_word(word)
                error_times = self.con.receive_error_times()
                tooltip("Misspell times: " + str(error_times))
                mw.reviewer._answerCard(error_times_to_ease(error_times))


def toggle_enable(action: QAction, state: State):
    if not state.is_enabled:
        try:
            if state.con is None:
                state.con = Connection()
            state.is_enabled = True
            action.setText("Enable qwerty ✓")
            gui_hooks.reviewer_did_show_answer.append(state.prompt_a_word)
            gui_hooks.profile_will_close.append(state.con.close)
        except ConnectionRefusedError:
            showInfo("Cannot connect to qwerty. Is it running?", title="qwerty addon")
    else:
        state.is_enabled = False
        action.setText("Enable qwerty")
        state.con.close()
        state.con = None
        gui_hooks.reviewer_did_show_answer.remove(state.prompt_a_word)


def main():
    state = State(is_enabled=False)

    config = mw.addonManager.getConfig(__name__)

    toggle_action = QAction("Enable qwerty", mw)
    qconnect(toggle_action.triggered, lambda: toggle_enable(toggle_action, state))
    mw.form.menuTools.addSeparator()
    mw.form.menuTools.addAction(toggle_action)


main()
