import sys

# Qt Core — для выравнивания и базовых вещей
from PySide6.QtCore import Qt

# Все UI-элементы
from PySide6.QtWidgets import *

from ui.main_window import MainWindow


# =========================
# ЗАПУСК ПРИЛОЖЕНИЯ
# =========================
app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())