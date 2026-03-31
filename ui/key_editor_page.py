from PySide6.QtCore import Qt
from PySide6.QtWidgets import *

from models.models import KeyInfo


# =========================
# ЭКРАН 2 — РЕДАКТОР КЛАВИШИ
# =========================
class KeyEditorPage(QWidget):
    def __init__(self, on_back, on_apply):
        super().__init__()

        # функция "назад"
        self.on_back = on_back
        self.on_apply = on_apply

        # текущая выбранная клавиша
        self.current_key_index = None

        self.build_ui()

    def build_ui(self):
        # внешний layout
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(30, 20, 30, 20)
        outer_layout.setSpacing(15)

        # ================= TOP BAR =================
        top_bar = QHBoxLayout()

        # кнопка назад
        back_btn = QPushButton("← Назад")
        back_btn.setFixedSize(120, 40)
        back_btn.clicked.connect(self.on_back)


        top_bar.addWidget(back_btn, alignment=Qt.AlignLeft)

        # заголовок
        self.title = QLabel("Введите")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
        """)

        top_bar.addWidget(self.title, stretch=1)

        # отступ справа (чтобы заголовок был по центру)
        top_bar.addSpacing(120)

        outer_layout.addLayout(top_bar)

        # ================= ОСНОВНОЙ БЛОК =================
        content_frame = QFrame()

        # фон большого серого блока
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #313131;
                border-radius: 30px;
            }
        """)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(30)

        # ================= ЛЕВАЯ ПАНЕЛЬ =================
        left_panel = QVBoxLayout()

        # кнопка "поменять картинку"
        image_btn = QPushButton("Поменять\nкартинку")
        image_btn.setFixedSize(250, 95)
    
        # кнопка "поменять назначение"
        assign_btn = QPushButton("Поменять\nназначение")
        assign_btn.setFixedSize(250, 95)
        left_panel.addWidget(image_btn)
        left_panel.addWidget(assign_btn)
        left_panel.addStretch()

        # ================= ПРАВАЯ ЧАСТЬ =================
        right_panel = QVBoxLayout()

        # тип действия
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Тип действия:"))
        self.action_type_combo = QComboBox()
        self.action_type_combo.addItems(["hotkey", "button", "macro"])
        type_row.addWidget(self.action_type_combo)
        type_row.addStretch()
        right_panel.addLayout(type_row)

        # список команд
        self.command_list = QListWidget()

        # делаем фон прозрачным (берёт цвет у content_frame)
        self.command_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
        """)

        # пример данных
        items = [
            "Ctrl+C  Копировать",
            "Ctrl+V  Вставить",
            "Ctrl+Z  Отменить",
            "Ctrl+Y  Вперед"
        ]

        for text in items:
            QListWidgetItem(text, self.command_list)
        self.command_list.itemClicked.connect(self.on_command_selected)

        right_panel.addWidget(self.command_list)

        # поля для формирования JSON
        form_layout = QFormLayout()
        self.keys_input = QLineEdit()
        self.keys_input.setPlaceholderText("Например: Ctrl+C или Ctrl+Shift+S")
        self.image_input = QLineEdit()
        self.image_input.setPlaceholderText("Путь до картинки (необязательно)")
        form_layout.addRow("Клавиши:", self.keys_input)
        form_layout.addRow("Картинка:", self.image_input)
        right_panel.addLayout(form_layout)

        # ================= НИЖНЯЯ КНОПКА =================
        bottom_bar = QHBoxLayout()
        bottom_bar.addStretch()

        apply_btn = QPushButton("установить")
        apply_btn.setFixedSize(300, 70)
        apply_btn.clicked.connect(self.apply_key_config)

        bottom_bar.addWidget(apply_btn)

        right_panel.addLayout(bottom_bar)

        # ================= СОБИРАЕМ ВСЁ =================
        content_layout.addLayout(left_panel, 1)
        content_layout.addLayout(right_panel, 3)

        content_frame.setLayout(content_layout)

        outer_layout.addWidget(content_frame)

        self.setLayout(outer_layout)

    # обновляем заголовок при выборе клавиши
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
            keys = [token for token in selected_item.text().split("  ")[0].split("+") if token]
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
