from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from models.models import KeyInfo

from models.models import KeyInfo


class KeyEditorPage(QWidget):
    """Экран редактирования выбранной клавиши."""

    def __init__(self, on_back, on_apply):
        super().__init__()
        self.on_back = on_back
        self.on_apply = on_apply
        self.current_key_index = None
        self.build_ui()

    def build_ui(self):
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(30, 20, 30, 20)
        outer_layout.setSpacing(15)

        top_bar = QHBoxLayout()
        back_btn = QPushButton("Назад")
        back_btn.setFixedSize(120, 40)
        back_btn.clicked.connect(self.on_back)
        top_bar.addWidget(back_btn, alignment=Qt.AlignLeft)

        self.title = QLabel("Введите")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(
            """
            font-size: 32px;
            font-weight: bold;
            """
        )
        top_bar.addWidget(self.title, stretch=1)
        top_bar.addSpacing(120)
        outer_layout.addLayout(top_bar)

        content_frame = QFrame()
        content_frame.setStyleSheet(
            """
            QFrame {
                background-color: #313131;
                border-radius: 30px;
            }
            """
        )
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(30)

        left_panel = QVBoxLayout()
        image_btn = QPushButton("Поменять\nкартинку")
        image_btn.setFixedSize(250, 95)
        assign_btn = QPushButton("Поменять\nназначение")
        assign_btn.setFixedSize(250, 95)
        left_panel.addWidget(image_btn)
        left_panel.addWidget(assign_btn)
        left_panel.addStretch()

        right_panel = QVBoxLayout()
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Тип действия:"))
        self.action_type_combo = QComboBox()
        self.action_type_combo.addItems(["hotkey", "button", "macro"])
        self.action_type_combo.currentTextChanged.connect(self.on_action_type_changed)
        type_row.addWidget(self.action_type_combo)
        type_row.addStretch()
        right_panel.addLayout(type_row)

        self.command_list = QListWidget()
        self.command_list.setStyleSheet(
            """
            QListWidget {
                background-color: transparent;
                border: none;
            }
            """
        )
        for text in [
            "Ctrl+C  Копировать",
            "Ctrl+V  Вставить",
            "Ctrl+Z  Отменить",
            "Ctrl+Y  Вперед",
        ]:
            QListWidgetItem(text, self.command_list)
        self.command_list.itemClicked.connect(self.on_command_selected)
        right_panel.addWidget(self.command_list)

        form_layout = QFormLayout()
        self.keys_input = QLineEdit()
        self.keys_input.setPlaceholderText("Например: Ctrl+C или Ctrl+Shift+S")
        self.image_input = QLineEdit()
        self.image_input.setPlaceholderText("Путь до картинки (необязательно)")
        form_layout.addRow("Клавиши:", self.keys_input)
        form_layout.addRow("Картинка:", self.image_input)
        right_panel.addLayout(form_layout)

        bottom_bar = QHBoxLayout()
        bottom_bar.addStretch()
        apply_btn = QPushButton("установить")
        apply_btn.setFixedSize(300, 70)
        apply_btn.clicked.connect(self.apply_key_config)
        bottom_bar.addWidget(apply_btn)
        right_panel.addLayout(bottom_bar)

        content_layout.addLayout(left_panel, 1)
        content_layout.addLayout(right_panel, 3)
        content_frame.setLayout(content_layout)
        outer_layout.addWidget(content_frame)

        self.setLayout(outer_layout)

    def set_key(self, key_index):
        self.current_key_index = key_index
        self.title.setText(f"Настройка Key {key_index + 1}")

    def apply_key_config(self):
        if self.current_key_index is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите клавишу.")
            return

        selected_item = self.command_list.currentItem()
        if self.keys_input.text().strip():
            keys = [part.strip() for part in self.keys_input.text().split("+") if part.strip()]
        elif selected_item:
            keys = self.extract_keys_from_item(selected_item)
        else:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Выберите команду из списка или введите комбинацию вручную.",
            )
            return

        key_info = KeyInfo(
            id=self.current_key_index + 1,
            action_type=self.action_type_combo.currentText(),
            keys=keys,
            image=self.image_input.text().strip(),
        )
        self.on_apply(key_info)

    def on_command_selected(self, item):
        keys = self.extract_keys_from_item(item)
        self.keys_input.setText("+".join(keys))

    def on_action_type_changed(self, action_type):
        is_hotkey = action_type == "hotkey"
        self.command_list.setVisible(is_hotkey)
        if not is_hotkey:
            self.command_list.clearSelection()

    @staticmethod
    def extract_keys_from_item(item):
        return [token.strip() for token in item.text().split("  ")[0].split("+") if token.strip()]
