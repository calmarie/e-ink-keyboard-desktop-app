from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from ui.key_editor_page import KeyEditorPage
from ui.key_select_page import KeySelectionPage

# =========================
# ГЛАВНОЕ ОКНО
# =========================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("E-Ink Keyboard")
        self.resize(1200, 700)

        # главный переключатель экранов
        self.stack = QStackedWidget()
        self.key_configs: dict[int, str] = {}

        # создаем страницы
        self.selection_page = KeySelectionPage(self.open_editor)
        self.editor_page = KeyEditorPage(self.go_back, self.save_key_config)

        # добавляем в стек
        self.stack.addWidget(self.selection_page)
        self.stack.addWidget(self.editor_page)

        self.setCentralWidget(self.stack)

        # фон всего окна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
        """)

    # открыть редактор
    def open_editor(self, key_index):
        self.editor_page.set_key(key_index)
        self.stack.setCurrentWidget(self.editor_page)

    # вернуться назад
    def go_back(self):
        self.stack.setCurrentWidget(self.selection_page)

    def save_key_config(self, key_info):
        payload = key_info.to_json()
        self.key_configs[key_info.id] = payload
        QMessageBox.information(
            self,
            f"Key {key_info.id}",
            "JSON сформирован (готов к отправке по Serial):\n\n" + payload,
        )
