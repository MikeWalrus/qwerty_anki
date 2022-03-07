from typing import *

from anki.cards import Card
from aqt import gui_hooks
from aqt import mw, operations
from aqt import qconnect
from aqt.qt import QAction, QMessageBox
from aqt.utils import showInfo, tooltip

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
    mb: Optional[QMessageBox]
    action: QAction

    def __init__(self, is_enabled: bool):
        self.is_enabled = is_enabled
        self.action = QAction("Enable qwerty", mw)
        qconnect(self.action.triggered, lambda: State.toggle_enable(self))
        mw.form.menuTools.addSeparator()
        mw.form.menuTools.addAction(self.action)
        self.con = None

    def disable(self):
        self.is_enabled = False
        self.action.setText("Enable qwerty")
        self.con.close()
        self.con = None
        gui_hooks.reviewer_did_show_answer.remove(self.prompt_a_word)

    def toggle_enable(self):
        if not self.is_enabled:
            try:
                if self.con is None:
                    self.con = Connection()
                self.is_enabled = True
                self.action.setText("Enable qwerty ✓")
                gui_hooks.reviewer_did_show_question.append(self.prompt_a_word)
                gui_hooks.profile_will_close.append(self.con.close)
            except ConnectionRefusedError:
                showInfo("Cannot connect to qwerty. Is it running?", title="qwerty addon")
        else:
            self.disable()

    def communicate(self, word: str, _c: Collection):
        self.con.send_word(word)
        return self.con.receive_error_times()

    def prompt_a_word(self, card: Card):
        items = card.note().items()
        for (k, v) in items:
            if k == "Back":
                word = v
                op = operations.QueryOp(op=lambda col: self.communicate(word, col),
                                        success=answer_the_card,
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
                title="qwerty addon")
            mw.deckBrowser.show()


def answer_the_card(error_times):
    mw.reviewer._showAnswer()
    tooltip("Misspell times: " + str(error_times))
    mw.reviewer._answerCard(error_times_to_ease(error_times))
    pass


def main():
    state = State(is_enabled=False)

    config = mw.addonManager.getConfig(__name__)


main()
