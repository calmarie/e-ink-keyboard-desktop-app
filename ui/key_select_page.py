from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from ui.theme import key_button_style, label_style, panel_style, title_style


class KeySelectionPage(QWidget):
    def __init__(self, on_key_selected):
        super().__init__()
        # Родитель передает callback, чтобы страница выбора не знала о навигации напрямую.
        self.on_key_selected = on_key_selected
        self.build_ui()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(56, 38, 56, 42)
        main_layout.setSpacing(16)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(6)

        title = QLabel("Выберите клавишу")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(title_style())
        header_layout.addWidget(title)

        subtitle = QLabel("Настройте любую из 3 e-ink клавиш")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(label_style(muted=True, size=18))
        header_layout.addWidget(subtitle)

        main_layout.addLayout(header_layout)

        content_frame = QFrame()
        content_frame.setStyleSheet(panel_style())
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(34, 34, 34, 34)
        content_layout.setSpacing(20)

        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(18)

        for i in range(3):
            btn = QPushButton(f"Клавиша {i + 1}")
            btn.setMinimumHeight(150)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setStyleSheet(key_button_style())
            # `x=i` фиксирует текущее значение цикла для каждой отдельной кнопки.
            btn.clicked.connect(lambda _, x=i: self.on_key_selected(x))
            buttons_layout.addWidget(btn)

        content_layout.addLayout(buttons_layout)
        main_layout.addWidget(content_frame, 1)
