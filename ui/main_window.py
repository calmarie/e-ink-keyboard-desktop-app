from PySide6.QtWidgets import QMessageBox, QMainWindow, QStackedWidget

from ui.key_editor_page import KeyEditorPage
from ui.key_pic_page import KeyPicPage
from ui.key_select_page import KeySelectionPage
from ui.theme import window_style
from conn.conn_com import send_packet

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("E-Ink Keyboard")
        self.resize(1200, 700)
        self.setMinimumSize(1080, 660)

        self.stack = QStackedWidget()
        self.key_configs: dict[int, str] = {}

        self.selection_page = KeySelectionPage(self.open_editor)
        self.editor_page = KeyEditorPage(
            self.go_back,
            self.send_key_config,
            self.open_image_picker,
        )
        self.pic_page = KeyPicPage(self.return_to_editor, self.apply_image_path)

        self.stack.addWidget(self.selection_page)
        self.stack.addWidget(self.editor_page)
        self.stack.addWidget(self.pic_page)

        self.setCentralWidget(self.stack)
        self.setStyleSheet(window_style())

    def open_editor(self, key_index):
        self.editor_page.set_key(key_index)
        self.stack.setCurrentWidget(self.editor_page)

    def open_image_picker(self):
        current_image = self.editor_page.image_input.text().strip()
        if current_image:
            self.pic_page.set_image_path(current_image)
        self.stack.setCurrentWidget(self.pic_page)

    def return_to_editor(self):
        self.stack.setCurrentWidget(self.editor_page)

    def go_back(self):
        self.stack.setCurrentWidget(self.selection_page)

    def apply_image_path(self, image_path: str):
        self.editor_page.set_image_path(image_path)
        self.return_to_editor()

    def send_key_config(self, key_info):
        
        QMessageBox.information(
            self,
            f"Key {key_info.id}",
            "JSON сформирован отправлен:",
            
        )
        send_packet(key_info.to_json())


        
