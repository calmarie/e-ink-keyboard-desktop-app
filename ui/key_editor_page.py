import eink
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

from models.key_info import KeyInfo
from ui.theme import (
    combo_style,
    label_style,
    line_edit_style,
    list_style,
    outline_button_style,
    panel_style,
    primary_button_style,
    side_button_style,
    title_style,
)


class KeyEditorPage(QWidget):
    def __init__(self, on_back, on_apply, on_change_image=None):
        super().__init__()
        self.on_back = on_back
        self.on_apply = on_apply
        self.on_change_image = on_change_image
        self.current_key_index = None
        self.build_ui()

    def build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(56, 38, 56, 42)
        outer_layout.setSpacing(28)

        top_bar = QHBoxLayout()

        self.back_btn = QPushButton("Назад")
        self.back_btn.setFixedSize(128, 44)
        self.back_btn.setStyleSheet(outline_button_style())
        self.back_btn.clicked.connect(self.on_back)
        top_bar.addWidget(self.back_btn, alignment=Qt.AlignLeft)

        self.title = QLabel("Настройка клавиши")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(title_style())
        top_bar.addWidget(self.title, stretch=1)
        top_bar.addSpacing(128)

        outer_layout.addLayout(top_bar)

        content_frame = QFrame()
        content_frame.setStyleSheet(panel_style())

        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(32)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(14)

        self.image_btn = QPushButton("поменять\nкартинку")
        self.image_btn.setFixedSize(250, 95)
        self.image_btn.setStyleSheet(side_button_style())
        self.image_btn.clicked.connect(self.open_image_picker)
        left_panel.addWidget(self.image_btn)

        self.assign_btn = QPushButton("поменять\nназначение")
        self.assign_btn.setFixedSize(250, 95)
        self.assign_btn.setStyleSheet(side_button_style(active=True))
        left_panel.addWidget(self.assign_btn)

        left_panel.addStretch()

        right_panel = QVBoxLayout()
        right_panel.setSpacing(18)

        type_row = QHBoxLayout()
        type_row.setSpacing(14)

        type_label = QLabel("Тип действия")
        type_label.setStyleSheet(label_style(muted=True))
        type_row.addWidget(type_label)

        self.action_type_combo = QComboBox()
        self.action_type_combo.addItems(["hotkey", "button", "macro"])
        self.action_type_combo.setStyleSheet(combo_style())
        self.action_type_combo.currentTextChanged.connect(self.on_action_type_changed)

        type_row.addWidget(self.action_type_combo)
        type_row.addStretch()
        right_panel.addLayout(type_row)

        self.command_list = QListWidget()
        self.command_list.setStyleSheet(list_style())
        self.command_list.setMinimumHeight(240)
        self.command_list.setMaximumHeight(320)
        for text in [
            "Ctrl+C  Копировать",
            "Ctrl+V  Вставить",
            "Ctrl+Z  Отменить",
            "Ctrl+Y  Повторить",
            "Ctrl+X  Вырезать",
            "Ctrl+A  Выделить всё",
            "Ctrl+S  Сохранить",
            "Ctrl+P  Печать",
            "Ctrl+F  Найти",
            "Ctrl+H  Заменить",
            "Ctrl+N  Новый файл / окно",
            "Ctrl+O  Открыть файл",
            "Ctrl+W  Закрыть вкладку",
            "Ctrl+T  Новая вкладка",
            "Ctrl+Shift+T  Восстановить закрытую вкладку",
            "Alt+Tab  Переключение между окнами",
            "Alt+F4  Закрыть окно",
            "Win+D  Показать рабочий стол",
            "Win+L  Заблокировать компьютер",
            "Win+E  Открыть проводник",
            "Win+R  Открыть окно Выполнить",
            "Ctrl+Shift+Esc  Диспетчер задач",
            "Ctrl+Alt+Del  Меню безопасности",
            "Ctrl+Backspace  Удалить слово слева",
            "Ctrl+Delete  Удалить слово справа",
            "Shift+Delete  Удалить без корзины",
            "Ctrl+Tab  Переключение вкладок",
            "Ctrl+Shift+Tab  Назад по вкладкам"
        ]:
            QListWidgetItem(text, self.command_list)
        self.command_list.itemClicked.connect(self.on_command_selected)
        right_panel.addWidget(self.command_list, 1)

        form_layout = QFormLayout()
        form_layout.setSpacing(14)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        keys_label = QLabel("Клавиши")
        keys_label.setStyleSheet(label_style(muted=True))

        image_label = QLabel("Картинка")
        image_label.setStyleSheet(label_style(muted=True))

        self.keys_input = QLineEdit()
        self.keys_input.setPlaceholderText("Например: Ctrl+C или Ctrl+Shift+S")
        self.keys_input.setStyleSheet(line_edit_style())

        self.image_input = QLineEdit()
        self.image_input.setPlaceholderText("Путь до картинки")
        self.image_input.setReadOnly(True)
        self.image_input.setStyleSheet(line_edit_style())

        form_layout.addRow(keys_label, self.keys_input)
        form_layout.addRow(image_label, self.image_input)
        right_panel.addLayout(form_layout)

        bottom_bar = QHBoxLayout()
        bottom_bar.addStretch()

        self.apply_btn = QPushButton("Установить")
        self.apply_btn.setFixedSize(320, 78)
        self.apply_btn.setStyleSheet(primary_button_style())
        self.apply_btn.clicked.connect(self.apply_key_config)
        bottom_bar.addWidget(self.apply_btn)

        right_panel.addStretch(1)
        right_panel.addLayout(bottom_bar)

        content_layout.addLayout(left_panel, 1)
        content_layout.addLayout(right_panel, 3)
        outer_layout.addWidget(content_frame)

    def set_key(self, key_index):
        self.current_key_index = key_index
        self.title.setText(f"Настройка клавиши {key_index + 1}")

    def set_image_path(self, image_path: str):
        self.image_input.setText(image_path)

    def open_image_picker(self):
        if self.on_change_image:
            self.on_change_image()

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

        image_path = self.image_input.text().strip()
        image_bytes: list[int] = []
        if image_path:
            try:
                image_bytes = list(eink.img2eink(image_path))
            except Exception as exc:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Не удалось преобразовать изображение:\n{exc}",
                )
                return

        key_info = KeyInfo(
            id=self.current_key_index + 1,
            action_type=self.action_type_combo.currentText(),
            keys=keys,
            image=image_bytes,
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
