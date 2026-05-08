from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QPushButton


class RightClickButton(QPushButton):
    def __init__(self, click_droit_callback):
        super().__init__()
        self.callback = click_droit_callback

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.RightButton:
            # Délai de 200ms pour corriger le bug où le clic droit reste bloqué.
            # Sans ce délai, il faut recliquer pour réinitialiser l’état du bouton.
            QTimer.singleShot(200, self.callback)
        super().mousePressEvent(e)


class ToolTipButton(QPushButton):
    def __init__(self, tool_tip: str, text: str = ""):
        super().__init__(text)
        self.tool_tip = tool_tip

    def enterEvent(self, event):
        self.setToolTip(self.tool_tip)
